from django.conf import settings
from django.db import models
from django.utils import timezone

def refund_receipt_upload_to(instance, filename):
    return f"refunds_receipts/{instance.pk or 'new'}/{filename}"

class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ("draft", "Entwurf"),
        ("submitted", "Eingereicht"),
        ("approved", "Genehmigt"),
        ("rejected", "Abgelehnt"),
        ("returned", "Zurückgegeben"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="refund_requests",
    )

    approver_function = models.ForeignKey(
        'iam.Function',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='refund_first_level',
        verbose_name="1. Entscheider (Funktion)",
    )

    cost_center = models.ForeignKey(
        'finance.CostCenter',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Kostenstelle",
        related_name="refund_requests",
    )

    cost_cluster = models.CharField(
        "Cluster",
        max_length=120,
        blank=True,
        default="",
        help_text="Demofeld; echte Verknüpfung auf Modell folgt später.",
    )

    receipt_date = models.DateField("Beleg vom")
    amount = models.DecimalField("Betrag (EUR)", max_digits=10, decimal_places=2)
    title = models.CharField("Bezeichnung", max_length=255)
    reason = models.TextField("Begründung", blank=True)

    receipt = models.FileField(
        "Beleg (PDF/JPG)",
        upload_to=refund_receipt_upload_to,
        null=True,
        blank=True
    )

    signature_name = models.CharField("Unterschrift (Name in Druckschrift)", max_length=200, blank=True, default="")
    signature_image = models.ImageField("Unterschrift (PNG)", upload_to=refund_receipt_upload_to, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    is_factually_correct = models.BooleanField("sachlich richtig", default=False)
    is_mathematically_correct = models.BooleanField("rechnerisch richtig", default=False)
    approver_comment = models.TextField("Bemerkungen (Genehmigung)", blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Erstattung #{self.pk or 'neu'} – {self.applicant} – {self.amount} €"
