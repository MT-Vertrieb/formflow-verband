
from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_home, name='settings_home'),
    path('smtp-test/', views.smtp_test, name='smtp_test'),
]
