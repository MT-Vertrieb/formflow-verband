from django import forms
from .models import InvoiceCheck


class InvoiceCheckForm(forms.ModelForm):
    class Meta:
        model = InvoiceCheck
        fields = [
            "approver_function",
            "cost_center",
            "supplier",
            "invoice_date",
            "total_amount",
            "pdf_link",
            "is_factually_correct",
            "is_mathematically_correct",
            "remarks",
            "cost_cluster",
        ]
        widgets = {
            "invoice_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
            "supplier": forms.TextInput(attrs={"class": "form-control"}),
            "pdf_link": forms.URLInput(attrs={"class": "form-control"}),
            "remarks": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "approver_function": forms.Select(attrs={"class": "form-select"}),
            "cost_center": forms.Select(attrs={"class": "form-select", "onchange": "updateClusters(this.value)"}),
            "cost_cluster": forms.Select(attrs={"class": "form-select"}),
        }
