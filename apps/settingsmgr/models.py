
from django.db import models

class SingletonModel(models.Model):
    class Meta:
        abstract = True
    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class GeneralSettings(SingletonModel):
    organization_name = models.CharField(max_length=200, blank=True, default='')
    logo_url = models.URLField(blank=True, default='')

class ThemeSettings(SingletonModel):
    primary_color = models.CharField(max_length=7, blank=True, default='#183153')
    accent_color = models.CharField(max_length=7, blank=True, default='#f3f4f6')
    sidebar_color = models.CharField(max_length=7, blank=True, default='#0f172a')
    text_color = models.CharField(max_length=7, blank=True, default='#111827')

class EmailTargets(SingletonModel):
    target_emails = models.CharField(max_length=500, blank=True, default='')  # semicolon separated

class SharePointSettings(SingletonModel):
    site_url = models.URLField(blank=True, default='')
    client_id = models.CharField(max_length=200, blank=True, default='')
    client_secret = models.CharField(max_length=200, blank=True, default='')
    library_name = models.CharField(max_length=200, blank=True, default='')

class MileageRate(models.Model):
    km_from = models.PositiveIntegerField()
    km_to = models.PositiveIntegerField(null=True, blank=True)  # None means open ended
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 0.30
    created_at = models.DateTimeField(auto_now_add=True)

class BudgetYear(models.Model):
    year = models.PositiveIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
