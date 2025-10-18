from django.urls import path
from . import views

urlpatterns = [
    path('import/', views.import_csv, name='finance_import'),
    path('overview/', views.overview_by_year, name='finance_overview'),
]
