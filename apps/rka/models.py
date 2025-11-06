from django.conf import settings
from django.db import models
from django.utils import timezone

def receipt_upload_to(instance, filename):
    return f"rka_receipts/{instance.travel_request_id}/{filename}"

class TravelRequest(models.Model):
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
        related_name="rka_requests",
    )

    approver_function = models.ForeignKey(
        'iam.Function',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='rka_first_level'
    )

    cost_center = models.ForeignKey(
        'finance.CostCenter',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    origin = models.CharField("Startort", max_length=255)
    destination = models.CharField("Zielort", max_length=255)
    purpose = models.CharField("Zweck der Reise", max_length=255, blank=True, default="")

    start_date = models.DateField("Startdatum")
    start_time = models.TimeField("Startzeit", null=True, blank=True)
    end_date = models.DateField("Enddatum")
    end_time = models.TimeField("Endzeit", null=True, blank=True)

    km_planned = models.PositiveIntegerField(
        "Geplante km (Routenplaner)", default=0, help_text="Ergebnis aus Routenplaner."
    )
    km_claimed = models.PositiveIntegerField(
        "Beantragte km", default=0, help_text="Vom Antragssteller eingetragene km."
    )
    km_deviation_reason = models.TextField(
        "Begründung Mehrkilometer",
        blank=True,
        help_text="Pflicht, falls Abweichung > Toleranz.",
    )

    destination_city = models.CharField(max_length=255, blank=True, default='')
    destination_street = models.CharField(max_length=255, blank=True, default='')
    destination_label = models.CharField(max_length=255, blank=True, default='')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"RKA #{self.pk or 'neu'} – {self.applicant}"

    @property
    def total_items(self):
        return sum((it.amount or 0) for it in self.items.all())

    @property
    def total(self):
        return self.total_items

class ExpenseItem(models.Model):
    travel_request = models.ForeignKey(
        TravelRequest, on_delete=models.CASCADE, related_name="items"
    )
    date = models.DateField("Datum")
    description = models.CharField("Beschreibung", max_length=255)
    amount = models.DecimalField("Betrag (EUR)", max_digits=10, decimal_places=2)
    receipt = models.FileField(
        "Beleg (PDF/JPG)", upload_to=receipt_upload_to, blank=True, null=True
    )

    class Meta:
        ordering = ["date", "id"]

    def __str__(self):
        return f"{self.date} – {self.description} ({self.amount} €)"
