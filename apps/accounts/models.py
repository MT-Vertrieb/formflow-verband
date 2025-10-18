from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def signature_upload_path(instance, filename):
    return f"signatures/user_{instance.user_id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Freigabe (Registrierungs-Workflow)
    is_approved = models.BooleanField(default=False)

    # Stammdaten
    first_name = models.CharField("Vorname", max_length=100, blank=True)
    last_name = models.CharField("Nachname", max_length=100, blank=True)
    street = models.CharField("Straße", max_length=200, blank=True)
    house_no = models.CharField("Hausnummer", max_length=20, blank=True)
    zip_code = models.CharField("PLZ", max_length=10, blank=True)
    city = models.CharField("Ort", max_length=120, blank=True)
    phone = models.CharField("Telefon", max_length=50, blank=True)

    # Bank
    account_holder = models.CharField("Kontoinhaber", max_length=200, blank=True)
    iban = models.CharField("IBAN", max_length=34, blank=True)
    bic = models.CharField("BIC", max_length=11, blank=True)
    bank_name = models.CharField("Bank", max_length=200, blank=True)

    # Unterschrift
    signature_image = models.ImageField("Digitale Unterschrift (JPG/PNG)", upload_to=signature_upload_path, blank=True, null=True)

    # Verbandsfunktionen (bis zu fünf; optional)
    # echte Modelle kommen aus apps.iam
    function_1 = models.ForeignKey('iam.Function', on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_func1')
    function_2 = models.ForeignKey('iam.Function', on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_func2')
    function_3 = models.ForeignKey('iam.Function', on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_func3')
    function_4 = models.ForeignKey('iam.Function', on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_func4')
    function_5 = models.ForeignKey('iam.Function', on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_func5')

    def __str__(self):
        return self.user.email or self.user.username

@receiver(post_save, sender=User)
def create_or_sync_profile(sender, instance, created, **kwargs):
    # Profil anlegen & Basisdaten synchronisieren
    if created:
        p = Profile.objects.create(
            user=instance,
            first_name=instance.first_name or "",
            last_name=instance.last_name or "",
        )
    else:
        try:
            p = instance.profile
            changed = False
            if instance.first_name and instance.first_name != p.first_name:
                p.first_name = instance.first_name; changed = True
            if instance.last_name and instance.last_name != p.last_name:
                p.last_name = instance.last_name; changed = True
            if changed:
                p.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance, first_name=instance.first_name or "", last_name=instance.last_name or "")
