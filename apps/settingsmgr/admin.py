from django.contrib import admin
from .models import GeneralSettings, ThemeSettings, EmailTargets, SharePointSettings, MileageRate, BudgetYear
admin.site.register([GeneralSettings, ThemeSettings, EmailTargets, SharePointSettings, MileageRate, BudgetYear])
