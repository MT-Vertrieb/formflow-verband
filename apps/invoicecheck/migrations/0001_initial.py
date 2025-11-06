# apps/invoicecheck/migrations/0001_initial.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("iam", "__first__"),
        ("finance", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvoiceCheck",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("supplier", models.CharField(max_length=255, verbose_name="Rechnungssteller")),
                ("invoice_date", models.DateField(verbose_name="Rechnung vom")),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Gesamtbetrag (€)")),
                ("pdf_link", models.URLField(blank=True, help_text="Link zur gespeicherten Rechnung auf SharePoint", verbose_name="PDF-Link (SharePoint)")),
                ("is_factually_correct", models.BooleanField(default=False, verbose_name="Sachlich richtig")),
                ("is_mathematically_correct", models.BooleanField(default=False, verbose_name="Rechnerisch richtig")),
                ("remarks", models.TextField(blank=True, verbose_name="Bemerkungen")),
                ("status", models.CharField(choices=[("draft", "Entwurf"), ("submitted", "Eingereicht"), ("approved", "Geprüft & Genehmigt"), ("rejected", "Abgelehnt")], default="draft", max_length=20)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("applicant", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoice_checks", to=settings.AUTH_USER_MODEL, verbose_name="Antragsteller")),
                ("approver_function", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="invoicecheck_approver", to="iam.function", verbose_name="1. Entscheider (Funktion)")),
                ("cost_center", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="finance.costcenter", verbose_name="Kostenstelle")),
                ("cost_cluster", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="finance.costcluster", verbose_name="Kostencluster")),
            ],
            options={
                "verbose_name": "Belegprüfung",
                "verbose_name_plural": "Belegprüfungen",
                "ordering": ["-created_at"],
            },
        ),
    ]
