from django.db import models
from django.conf import settings
from django.utils import timezone


class InvoiceCheck(models.Model):
    STATUS_CHOICES = [
        ("draft", "Entwurf"),
        ("submitted", "Eingereicht"),
        ("approved", "Geprüft & Genehmigt"),
        ("rejected", "Abgelehnt"),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invoice_checks",
        verbose_name="Antragsteller",
    )
    approver_function = models.ForeignKey(
        "iam.Function",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoicecheck_approver",
        verbose_name="1. Entscheider (Funktion)",
    )
    cost_center = models.ForeignKey(
        "finance.CostCenter",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Kostenstelle",
    )

    # Eingabefelder
    supplier = models.CharField("Rechnungssteller", max_length=255)
    invoice_date = models.DateField("Rechnung vom")
    total_amount = models.DecimalField("Gesamtbetrag (€)", max_digits=10, decimal_places=2)

    pdf_link = models.URLField("PDF-Link (SharePoint)", blank=True, help_text="Link zur gespeicherten Rechnung auf SharePoint")

    # Genehmigung / Prüferbereich
    is_factually_correct = models.BooleanField("Sachlich richtig", default=False)
    is_mathematically_correct = models.BooleanField("Rechnerisch richtig", default=False)
    remarks = models.TextField("Bemerkungen", blank=True)

    # Zuordnung Cluster (abhängig von Kostenstelle)
    cost_cluster = models.ForeignKey(
        "finance.CostCluster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Kostencluster",
    )

    # Systemfelder
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Belegprüfung"
        verbose_name_plural = "Belegprüfungen"

    def __str__(self):
        return f"Belegprüfung #{self.pk or 'neu'} – {self.applicant}"
