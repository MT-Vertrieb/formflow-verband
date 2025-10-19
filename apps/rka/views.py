from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest

from apps.iam.models import Function
from apps.settingsmgr.utils import (
    get_module_config,
    recipients_list,
    build_archive_mail_preview,
)
from .models import TravelRequest, ApprovalEvent
from .pdf import build_final_pdf_bytes


def _client_ip(request):
    h = request.META.get("HTTP_X_FORWARDED_FOR")
    if h:
        return h.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or ""


@login_required
def new_request(request):
    if request.method == "POST":
        fn_id = request.POST.get("step1_function")
        try:
            fn = Function.objects.get(id=fn_id)
        except (Function.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Bitte Entscheider Nr. 1 auswählen.")
            return redirect("rka_new")

        tr = TravelRequest.objects.create(applicant=request.user, step1_function=fn, status="IN_REVIEW")
        messages.success(request, f"Reisekostenantrag #{tr.id} angelegt. Genehmigungsprozess gestartet.")
        return redirect("rka_detail", pk=tr.id)

    functions = Function.objects.all().order_by("name")
    return render(request, "rka/new.html", {"functions": functions})


@login_required
def detail(request, pk: int):
    tr = get_object_or_404(TravelRequest, pk=pk)

    seq = tr.approval_sequence()
    cfg = get_module_config("RKA")
    archive_to = recipients_list(cfg)
    current_fn = tr.current_function()

    return render(
        request,
        "rka/detail.html",
        {
            "tr": tr,
            "sequence": seq,
            "events": tr.events.all(),
            "current_fn": current_fn,
            "archive_to": archive_to,
            "is_final_after_next": tr.is_final_approval_after_next(),
        },
    )


@login_required
def act_on_request(request, pk: int, action: str):
    """
    Aktion auf den aktuellen Schritt: APPROVE / RETURN / REJECT
    – protokolliert ein ApprovalEvent
    – aktualisiert Status
    – erzeugt KEIN PDF und versendet NICHTS (Variante A)
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Nur POST erlaubt.")

    action = action.upper()
    if action not in ("APPROVE", "RETURN", "REJECT"):
        return HttpResponseBadRequest("Ungültige Aktion.")

    tr = get_object_or_404(TravelRequest, pk=pk)

    # wer ist am Zug?
    current_fn = tr.current_function()
    if not current_fn:
        messages.info(request, "Kein weiterer Schritt offen.")
        return redirect("rka_detail", pk=tr.id)

    # Schritt-Nummer & Logging
    step_no = tr.current_step_number()
    ApprovalEvent.objects.create(
        request=tr,
        step_number=step_no,
        function=current_fn,
        actor=request.user,  # in echt: prüfen, ob actor dieser Funktion zugeordnet ist
        decision=action,
        comment=request.POST.get("comment", "").strip(),
        ip_address=_client_ip(request),
    )

    # Status-Logik
    if action == "APPROVE":
        # war dies der letzte notwendige Schritt?
        if tr.is_final_approval_after_next():
            tr.status = "APPROVED"
            tr.save()
            messages.success(request, f"RKA #{tr.id} final genehmigt. (PDF/Versand folgt separat.)")
            return redirect("rka_detail", pk=tr.id)
        else:
            tr.status = "IN_REVIEW"
            tr.save()
            messages.success(request, f"Schritt {step_no} genehmigt. Nächster Schritt ist fällig.")
            return redirect("rka_detail", pk=tr.id)

    if action == "RETURN":
        tr.status = "RETURNED"
        tr.save()
        messages.warning(request, f"RKA #{tr.id} wurde zur Korrektur zurückgegeben.")
        return redirect("rka_detail", pk=tr.id)

    if action == "REJECT":
        tr.status = "REJECTED"
        tr.save()
        messages.error(request, f"RKA #{tr.id} wurde abgelehnt.")
        return redirect("rka_detail", pk=tr.id)

    return redirect("rka_detail", pk=tr.id)


@login_required
def finalize_preview(request, pk: int):
    """
    Zeigt NUR eine Vorschau, welche E-Mail beim Abschluss versendet würde.
    (Kein Versand, keine PDF.)
    """
    tr = get_object_or_404(TravelRequest, pk=pk)
    seq = tr.approval_sequence()
    cfg = get_module_config("RKA")
    preview = build_archive_mail_preview(tr, seq, cfg)

    return render(
        request,
        "rka/detail.html",
        {
            "tr": tr,
            "sequence": seq,
            "events": tr.events.all(),
            "current_fn": tr.current_function(),
            "archive_to": preview["recipients"],
            "final_preview": preview,
            "is_final_after_next": tr.is_final_approval_after_next(),
        },
    )


@login_required
def download_final_pdf(request, pk: int):
    """
    Gibt die finale PDF aus (nur wenn der Antrag APPROVED ist).
    Kein Versand – reiner Download/Stream.
    """
    tr = get_object_or_404(TravelRequest, pk=pk)
    if tr.status != "APPROVED":
        messages.error(request, "PDF ist erst nach finaler Genehmigung verfügbar.")
        return redirect("rka_detail", pk=tr.id)

    pdf_bytes = build_final_pdf_bytes(tr)
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="RKA_{tr.pk}.pdf"'
    return resp
