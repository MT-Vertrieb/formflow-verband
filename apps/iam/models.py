from django.db import models
from django.contrib.auth.models import User

class Function(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Kurzcode, z. B. PRAES, GS, VPFIN")
    name = models.CharField(max_length=200, help_text="Anzeigename der Verbandsfunktion")

    class Meta:
        verbose_name = "Verbandsfunktion"
        verbose_name_plural = "Verbandsfunktionen"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


# Module-Auswahl: deckt deine Bausteine + GLOBAL ab
MODULE_CHOICES = [
    ("GLOBAL", "Global"),
    ("PERSOENLICH", "Persönlicher Bereich"),
    ("BENUTZER", "Benutzerverwaltung"),
    ("KALENDER", "Vereins/Verbandskalender"),
    ("RKA", "Reisekostenantrag"),
    ("SKE", "Sachkostenerstattung"),
    ("HON", "Honorarabrechnung"),
    ("BELEG", "Genehmigung von Belegen"),
    ("HAUPLAN", "Haushaltsplanung"),
    ("FAHRZEUG", "Verwaltung von Fahrzeugen"),
    ("ARBEITSZEIT", "Arbeitszeitdokumentation"),
    ("ARBEITSURLAUB", "Arbeits- und Urlaubsplan"),
    ("DESK", "Desksharing"),
    ("SETTINGS", "Systemeinstellungen"),
]

ROLE_CHOICES_HELP = """
Empfohlene Codes:
- SYSTEMADMIN (nur GLOBAL/SETTINGS sinnvoll)
- ANTRAGSTELLER
- ANTRAGSBEARBEITER
- BEARBEITER
- HHP_READ_ALL / HHP_READ_ASSIGNED / HHP_WRITE_ASSIGNED / HHP_WRITE_ALL (für Haushaltsplan)
"""

class Role(models.Model):
    module = models.CharField(max_length=32, choices=MODULE_CHOICES)
    code = models.CharField(max_length=50, help_text="z. B. ANTRAGSTELLER, ANTRAGSBEARBEITER, SYSTEMADMIN")
    name = models.CharField(max_length=200, help_text="Lesbarer Rollenname")
    description = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("module", "code")
        verbose_name = "Rolle"
        verbose_name_plural = "Rollen"
        ordering = ["module", "name"]

    def __str__(self):
        return f"{self.get_module_display()} – {self.name} ({self.code})"


class ModuleRoleAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_roles")
    module = models.CharField(max_length=32, choices=MODULE_CHOICES)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="assignments")
    # Platzhalter für spätere Scopes (z. B. Kostenstellenliste) – für jetzt leer lassen
    scope_json = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "module")  # pro Modul genau eine Rolle pro Nutzer
        verbose_name = "Rollen-Zuweisung"
        verbose_name_plural = "Rollen-Zuweisungen"

    def __str__(self):
        return f"{self.user} → {self.get_module_display()} = {self.role.code}"
