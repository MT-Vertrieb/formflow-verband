# apps/invoicecheck/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.apps import apps as django_apps

from .models import InvoiceCheck
from .forms import InvoiceCheckForm


@login_required
def invoicecheck_list(request):
    """Liste aller Belegprüfungen des angemeldeten Nutzers."""
    checks = InvoiceCheck.objects.filter(applicant=request.user).order_by("-created_at")
    return render(request, "invoicecheck/list.html", {"checks": checks})


@login_required
def invoicecheck_new(request):
    """Neuer Antrag für Belegprüfung."""
    if request.method == "POST":
        form = InvoiceCheckForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.applicant = request.user
            # Optional: Absende-Status setzen, wenn Button 'Absenden' benutzt wurde
            if request.POST.get("action") == "submit":
                obj.status = "submitted"
            obj.save()
            messages.success(request, "Belegprüfung erfolgreich angelegt.")
            return redirect("invoicecheck:list")
    else:
        form = InvoiceCheckForm()
    return render(request, "invoicecheck/form.html", {"form": form, "mode": "new"})


@login_required
def invoicecheck_edit(request, pk):
    """Bearbeiten eines bestehenden Antrags."""
    obj = get_object_or_404(InvoiceCheck, pk=pk, applicant=request.user)
    if request.method == "POST":
        form = InvoiceCheckForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            if request.POST.get("action") == "submit":
                obj.status = "submitted"
            obj.save()
            messages.success(request, "Belegprüfung aktualisiert.")
            return redirect("invoicecheck:list")
    else:
        form = InvoiceCheckForm(instance=obj)
    return render(request, "invoicecheck/form.html", {"form": form, "mode": "edit", "obj": obj})


@login_required
def clusters_by_cost_center(request):
    """
    JSON-Endpoint: liefert die CostClusters zur übergebenen Kostenstelle (?cc=<id>).
    Versucht mehrere gängige Relationsnamen robust abzufangen und fällt, falls nichts
    gefunden wird, auf alle Cluster zurück (Demo-Zweck).
    """
    cc_id = request.GET.get("cc")
    CostCenter = django_apps.get_model("finance", "CostCenter")
    CostCluster = django_apps.get_model("finance", "CostCluster")

    if not CostCenter or not CostCluster:
        # finance-Modelle nicht verfügbar -> leere Liste zurück (verhindert 500er)
        return JsonResponse({"results": []})

    clusters_qs = CostCluster.objects.none()

    if cc_id:
        try:
            cc = CostCenter.objects.get(pk=cc_id)
        except CostCenter.DoesNotExist:
            raise Http404("Kostenstelle nicht gefunden")

        # 1) Versuch: Reverse-Relation von CostCenter -> Cluster (häufig: 'clusters' o.ä.)
        for rel_name in ["clusters", "cost_clusters", "costcluster_set", "cost_clusters_set"]:
            rel = getattr(cc, rel_name, None)
            if rel is not None:
                try:
                    qs = rel.all()
                    # Wenn es diese Relation gibt, übernehmen (auch wenn 0 Ergebnisse)
                    clusters_qs = qs
                    break
                except Exception:
                    pass

        # 2) Versuch: FK auf Cluster-Seite (z.B. cost_center oder costcenter)
        if clusters_qs is None or not clusters_qs.exists():
            # Namen aller relationalen Felder auf Cluster zusammensuchen
            fk_names = [f.name for f in CostCluster._meta.fields if f.is_relation]
            for fk in ["cost_center", "costcenter"]:
                if fk in fk_names:
                    try:
                        clusters_qs = CostCluster.objects.filter(**{fk: cc})
                        break
                    except Exception:
                        pass

        # 3) Versuch: M2M auf Cluster-Seite (z.B. cost_centers)
        if clusters_qs is None or not clusters_qs.exists():
            m2m_names = [m.name for m in CostCluster._meta.many_to_many]
            for m2m in ["cost_centers", "costcenter_set"]:
                if m2m in m2m_names:
                    try:
                        clusters_qs = CostCluster.objects.filter(**{m2m: cc})
                        break
                    except Exception:
                        pass

    # Fallback (Demo): Falls nichts gefunden wurde, alle Cluster anbieten
    if clusters_qs is None or not clusters_qs.exists():
        clusters_qs = CostCluster.objects.all().order_by("id")[:200]

    data = [{"id": c.pk, "label": str(c)} for c in clusters_qs]
    return JsonResponse({"results": data})
