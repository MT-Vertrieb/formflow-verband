from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.new_request, name="rka_new"),
    path("detail/<int:pk>/", views.detail, name="rka_detail"),
    path("act/<int:pk>/<str:action>/", views.act_on_request, name="rka_act"),
    path("finalize/<int:pk>/", views.finalize_preview, name="rka_finalize_preview"),
    path("final-pdf/<int:pk>/", views.download_final_pdf, name="rka_final_pdf"),
]
