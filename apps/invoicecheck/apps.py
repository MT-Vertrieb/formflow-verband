# apps/invoicecheck/apps.py
from django.apps import AppConfig


class InvoicecheckConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.invoicecheck"
    verbose_name = "Belegprüfung"
