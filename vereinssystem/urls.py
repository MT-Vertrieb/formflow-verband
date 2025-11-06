from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts
    path('accounts/', include('apps.accounts.urls')),

    # Settings / Finance
    path('settingsmgr/', include('apps.settingsmgr.urls')),
    path('finance/', include('apps.finance.urls')),

    # Reisekostenantrag
    path('rka/', include('apps.rka.urls')),

    # Erstattung von Beträgen – mit Namespace
    path(
        'refunds/',
        include(('apps.refunds.urls', 'refunds'), namespace='refunds')
    ),

    # Belegprüfung – mit Namespace (fix für {% url 'invoicecheck:clusters' %})
    path(
        'invoicecheck/',
        include(('apps.invoicecheck.urls', 'invoicecheck'), namespace='invoicecheck')
    ),

    # Dashboard
    path('', TemplateView.as_view(template_name='core/dashboard.html'), name='dashboard'),
]

# Media (Uploads) in der Entwicklung ausliefern
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
