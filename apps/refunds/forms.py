from django import forms
from .models import RefundRequest

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = [
            "approver_function", "cost_center", "cost_cluster",
            "receipt_date", "amount", "title", "reason",
            "receipt",
        ]
        widgets = {
            "receipt_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
        }
