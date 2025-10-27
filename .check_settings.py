import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','vereinssystem.settings')
django.setup()
import django as dj
from django.conf import settings
print('Django:', dj.get_version())
print('DEBUG:', settings.DEBUG)
print('EMAIL_USE_TLS:', settings.EMAIL_USE_TLS, 'EMAIL_USE_SSL:', settings.EMAIL_USE_SSL)
