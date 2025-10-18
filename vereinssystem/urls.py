
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('settingsmgr/', include('apps.settingsmgr.urls')),
    path('finance/', include('apps.finance.urls')),
    path('', TemplateView.as_view(template_name='core/dashboard.html'), name='dashboard'),
]
