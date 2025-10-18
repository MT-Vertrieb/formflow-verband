
from django import forms
from .models import GeneralSettings, ThemeSettings, EmailTargets, SharePointSettings, MileageRate, BudgetYear

class GeneralSettingsForm(forms.ModelForm):
    class Meta:
        model = GeneralSettings
        fields = ['organization_name','logo_url']

class ThemeSettingsForm(forms.ModelForm):
    class Meta:
        model = ThemeSettings
        fields = ['primary_color','accent_color','sidebar_color','text_color']

class EmailTargetsForm(forms.ModelForm):
    class Meta:
        model = EmailTargets
        fields = ['target_emails']

class SharePointSettingsForm(forms.ModelForm):
    class Meta:
        model = SharePointSettings
        fields = ['site_url','client_id','client_secret','library_name']

class MileageRateForm(forms.ModelForm):
    class Meta:
        model = MileageRate
        fields = ['km_from','km_to','rate']

class BudgetYearForm(forms.ModelForm):
    class Meta:
        model = BudgetYear
        fields = ['year']
