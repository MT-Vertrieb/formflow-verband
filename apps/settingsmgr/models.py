from django.db import models
from django.core.validators import MinValueValidator
from apps.iam.models import Function  # Funktionen steuern Sicht/Genehmigung

# -------------------------------------------------
# Singleton-Basisklasse für einfache Einstellungsseiten
# -------------------------------------------------
class SingletonModel(models.Model):
    class Meta:
        abstract = True
    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

# -------------------------------------------------
# Allgemeine/Theme/Email/SharePoint-Einstellungen
# -------------------------------------------------
class GeneralSettings(SingletonModel):
    organization_name = models.CharField(max_length=200, blank=True, default='')
    logo_url = models.URLField(blank=True, default='')

class ThemeSettings(SingletonModel):
    primary_color = models.CharField(max_length=7, blank=True, default='#183153')
    accent_color = models.CharField(max_length=7, blank=True, default='#f3f4f6')
    sidebar_color = models.CharField(max_length=7, blank=True, default='#0f172a')
    text_color = models.CharField(max_length=7, blank=True, default='#111827')

class EmailTargets(SingletonModel):
    # Semikolon-getrennte Liste – Validierung/Parsing beim Versand
    target_emails = models.CharField(max_length=500, blank=True, default='')

class SharePointSettings(SingletonModel):
    site_url = models.URLField(blank=True, default='')
    client_id = models.CharField(max_length=200, blank=True, default='')
    client_secret = models.CharField(max_length=200, blank=True, default='')
    library_name = models.CharField(max_length=200, blank=True, default='')

# -------------------------------------------------
# Kilometerpauschalen & Haushaltsjahr (falls benötigt)
# -------------------------------------------------
class MileageRate(models.Model):
    km_from = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    km_to = models.PositiveIntegerField(null=True, blank=True)  # None = offen
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # z. B. 0.30
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["km_from"]

    def __str__(self):
        if self.km_to is None:
            return f"{self.km_from}+ km → {self.rate} €/km"
        return f"{self.km_from}-{self.km_to} km → {self.rate} €/km"

class BudgetYear(models.Model):
    year = models.PositiveIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["year"]

    def __str__(self):
        return str(self.year)

# -------------------------------------------------
# Feste Genehmigungsreihenfolge pro Modul (ohne Jahr!)
# Schritt 1 wählt Antragsteller im Formular; 2–5 hier konfigurierbar (optional).
# Nach letztem vorhandenem Schritt: PDF erzeugen & an archive_recipients senden.
# -------------------------------------------------
MODULE_CHOICES = [
    ("RKA", "Reisekostenantrag"),
    ("SKE", "Sachkostenerstattung"),
    ("HON", "Honorarabrechnung"),
    ("GBL", "Genehmigung von Belegen"),
]

class ModuleApprovalConfig(models.Model):
    module = models.CharField(max_length=4, choices=MODULE_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)

    # Entscheider 2–5 (optional; leere werden später übersprungen)
    step2_function = models.ForeignKey(
        Function, on_delete=models.PROTECT, null=True, blank=True,
        related_name="approval_step2_for",
        help_text="Entscheider Nr. 2 (optional)"
    )
    step3_function = models.ForeignKey(
        Function, on_delete=models.PROTECT, null=True, blank=True,
        related_name="approval_step3_for",
        help_text="Entscheider Nr. 3 (optional)"
    )
    step4_function = models.ForeignKey(
        Function, on_delete=models.PROTECT, null=True, blank=True,
        related_name="approval_step4_for",
        help_text="Entscheider Nr. 4 (optional)"
    )
    step5_function = models.ForeignKey(
        Function, on_delete=models.PROTECT, null=True, blank=True,
        related_name="approval_step5_for",
        help_text="Entscheider Nr. 5 (optional)"
    )

    # mehrere Empfänger per Semikolon; wir splitten beim Versand
    archive_recipients = models.CharField(
        max_length=1000,
        help_text="Ablage-E-Mail(s); mehrere durch Semikolon trennen"
    )

    class Meta:
        ordering = ["module"]

    def __str__(self):
        return f"{self.get_module_display()} – feste Kette"

    def step_functions(self, step1_function):
        """Effektive Reihenfolge: [step1, step2?, step3?, step4?, step5?] ohne Nones."""
        seq = [step1_function, self.step2_function, self.step3_function, self.step4_function, self.step5_function]
        return [f for f in seq if f]

    def recipients_list(self):
        """Semikolonliste → Python-Liste (getrimmt, leere entfernt)."""
        return [p.strip() for p in (self.archive_recipients or "").split(";") if p.strip()]
