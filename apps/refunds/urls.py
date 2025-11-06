from django.urls import path
from . import views

app_name = "refunds"

urlpatterns = [
    path("", views.refund_list, name="list"),
    path("new/", views.refund_new, name="new"),
    path("<int:pk>/edit/", views.refund_edit, name="edit"),
]
