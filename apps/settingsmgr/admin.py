from django.contrib import admin
from .models import (
    GeneralSettings, ThemeSettings, EmailTargets, SharePointSettings,
    MileageRate, BudgetYear, ModuleApprovalConfig
)

# Singleton-Einstellungen schlicht registrieren
admin.site.register([GeneralSettings, ThemeSettings, EmailTargets, SharePointSettings, MileageRate, BudgetYear])

@admin.register(ModuleApprovalConfig)
class ModuleApprovalConfigAdmin(admin.ModelAdmin):
    list_display = ("module", "is_active", "archive_recipients")
    list_filter = ("module", "is_active")
    search_fields = ("archive_recipients",)
    fieldsets = (
        (None, {
            "fields": ("module", "is_active")
        }),
        ("Feste Genehmigungsreihenfolge", {
            "fields": ("step2_function", "step3_function", "step4_function", "step5_function"),
            "description": "Schritt 1 setzt der Antragsteller im Formular. Leere Schritte werden übersprungen."
        }),
        ("Ablage", {
            "fields": ("archive_recipients",),
            "description": "Zentrale E-Mail(s) für die finale PDF; mehrere per Semikolon."
        }),
    )
