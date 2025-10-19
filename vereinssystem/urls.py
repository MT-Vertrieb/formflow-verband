from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('settingsmgr/', include('apps.settingsmgr.urls')),
    path('finance/', include('apps.finance.urls')),
    path('', TemplateView.as_view(template_name='core/dashboard.html'), name='dashboard'),
    path("rka/", include("apps.rka.urls")),
]

# Media (Uploads) in der Entwicklung ausliefern
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
