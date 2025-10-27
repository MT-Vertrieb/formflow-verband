from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.rka_new, name="rka_new"),
    path("edit/<int:pk>/", views.rka_edit, name="rka_edit"),
    path("", views.rka_list, name="rka_list"),
]
