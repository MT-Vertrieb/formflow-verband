from django.urls import path
from . import views

app_name = "invoicecheck"

urlpatterns = [
    path("", views.invoicecheck_list, name="list"),
    path("new/", views.invoicecheck_new, name="new"),
    path("<int:pk>/edit/", views.invoicecheck_edit, name="edit"),

    # JSON-Endpoint für Cluster-Liste
    # Hauptname wie im Template verwendet:
    path("clusters/", views.clusters_by_cost_center, name="clusters"),
    # Alias (falls woanders noch der alte Name verwendet wird):
    path(
        "clusters-by-cost-center/",
        views.clusters_by_cost_center,
        name="clusters_by_cost_center",
    ),
]
