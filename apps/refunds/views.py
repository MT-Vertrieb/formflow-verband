from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from django import forms
import json

from .models import RefundRequest
from apps.finance.models import CostCenter, CostCluster


class RefundForm(forms.ModelForm):
    # Nicht-modellgebundenes Feld für die Unterschrift (Canvas Base64)
    signature_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RefundRequest
        fields = [
            "approver_function",
            "cost_center",
            "receipt_date",
            "amount",
            "title",
            "reason",
            # WICHTIG: signature_data NICHT in Meta.fields, da kein DB-Feld
        ]
        widgets = {
            "receipt_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }


@login_required
def refund_list(request):
    qs = (
        RefundRequest.objects
        .select_related("applicant", "cost_center")
        .order_by("-created_at")
    )
    return render(request, "refunds/list.html", {"requests": qs})


@login_required
@transaction.atomic
def refund_new(request):
    if request.method == "POST":
        form = RefundForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.applicant = request.user

            # Optional: signature_data ist verfügbar, wird aber (noch) nicht persistiert
            # sig_b64 = form.cleaned_data.get("signature_data")

            if "submit_request" in request.POST:
                obj.status = RefundRequest.STATUS_SUBMITTED
                messages.success(request, "Erstattungsantrag eingereicht.")
            else:
                obj.status = RefundRequest.STATUS_DRAFT
                messages.success(request, "Erstattungsantrag gespeichert (Entwurf).")

            obj.save()
            return redirect("refunds:list")
    else:
        form = RefundForm()

    context = {"form": form}
    context.update(_clusters_mapping_context())
    return render(request, "refunds/edit.html", context)


@login_required
@transaction.atomic
def refund_edit(request, pk):
    obj = get_object_or_404(RefundRequest, pk=pk, applicant=request.user)
    if request.method == "POST":
        form = RefundForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            # sig_b64 = form.cleaned_data.get("signature_data")

            if "submit_request" in request.POST:
                obj.status = RefundRequest.STATUS_SUBMITTED
                messages.success(request, "Erstattungsantrag eingereicht.")
            else:
                messages.success(request, "Erstattungsantrag gespeichert.")

            obj.save()
            return redirect("refunds:list")
    else:
        form = RefundForm(instance=obj)

    context = {"form": form, "obj": obj}
    context.update(_clusters_mapping_context())
    return render(request, "refunds/edit.html", context)


def _clusters_mapping_context():
    """
    Stellt dem Template ein Mapping bereit:
    clusters_by_cc_json = {
        <cost_center_id>: [{ "id": <cluster_id>, "name": "<Clustername>" }, ...],
        ...
    }
    """
    clusters_by_cc = {}
    for cl in CostCluster.objects.select_related("cost_center").all():
        cc_id = getattr(cl, "cost_center_id", None)
        if cc_id is None:
            continue
        clusters_by_cc.setdefault(cc_id, []).append({
            "id": cl.id,
            "name": getattr(cl, "name", str(cl)),
        })

    return {
        "clusters_by_cc_json": json.dumps(clusters_by_cc, cls=DjangoJSONEncoder),
    }
