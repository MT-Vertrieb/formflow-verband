from django.contrib import admin
from .models import InvoiceCheck


@admin.register(InvoiceCheck)
class InvoiceCheckAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "applicant",
        "supplier",
        "invoice_date",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "invoice_date",
        "created_at",
        "cost_center",
        "cost_cluster",
    )
    search_fields = (
        "supplier",
        "remarks",
        "applicant__username",
        "applicant__first_name",
        "applicant__last_name",
        "applicant__email",
    )
    # Kein autocomplete_fields -> sonst braucht's zusätzliche Admin-Konfigs
    raw_id_fields = ("approver_function", "cost_center", "cost_cluster")
    date_hierarchy = "invoice_date"
    ordering = ("-created_at",)
