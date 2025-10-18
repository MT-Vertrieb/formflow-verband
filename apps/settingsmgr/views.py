
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from .models import GeneralSettings, ThemeSettings, EmailTargets, SharePointSettings, MileageRate, BudgetYear
from .forms import GeneralSettingsForm, ThemeSettingsForm, EmailTargetsForm, SharePointSettingsForm, MileageRateForm, BudgetYearForm

def admin_required(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_required)
def settings_home(request):
    gen = GeneralSettings.get_solo()
    theme = ThemeSettings.get_solo()
    emails = EmailTargets.get_solo()
    sp = SharePointSettings.get_solo()
    if request.method == 'POST':
        if 'save_general' in request.POST:
            form = GeneralSettingsForm(request.POST, instance=gen)
            if form.is_valid():
                form.save(); messages.success(request, 'Allgemeine Einstellungen gespeichert.')
                return redirect('settings_home')
        if 'save_theme' in request.POST:
            form = ThemeSettingsForm(request.POST, instance=theme)
            if form.is_valid():
                form.save(); messages.success(request, 'Theme gespeichert.')
                return redirect('settings_home')
        if 'save_emails' in request.POST:
            form = EmailTargetsForm(request.POST, instance=emails)
            if form.is_valid():
                form.save(); messages.success(request, 'E-Mail-Ziele gespeichert.')
                return redirect('settings_home')
        if 'save_sp' in request.POST:
            form = SharePointSettingsForm(request.POST, instance=sp)
            if form.is_valid():
                form.save(); messages.success(request, 'SharePoint-Einstellungen gespeichert.')
                return redirect('settings_home')
        if 'add_rate' in request.POST:
            form = MileageRateForm(request.POST)
            if form.is_valid():
                form.save(); messages.success(request, 'Kilometersatz hinzugefügt.')
                return redirect('settings_home')
        if 'add_year' in request.POST:
            form = BudgetYearForm(request.POST)
            if form.is_valid():
                form.save(); messages.success(request, 'Haushaltsjahr hinzugefügt.')
                return redirect('settings_home')
    ctx = {
        'gen_form': GeneralSettingsForm(instance=gen),
        'theme_form': ThemeSettingsForm(instance=theme),
        'emails_form': EmailTargetsForm(instance=emails),
        'sp_form': SharePointSettingsForm(instance=sp),
        'rates': MileageRate.objects.all().order_by('km_from'),
        'rate_form': MileageRateForm(),
        'years': BudgetYear.objects.all().order_by('year'),
        'year_form': BudgetYearForm(),
    }
    return render(request, 'settingsmgr/home.html', ctx)

@login_required
@user_passes_test(admin_required)
def smtp_test(request):
    if request.method == 'POST':
        to = request.POST.get('to','').strip()
        subject = 'SMTP-Test: Vereinssystem'
        body = 'Dies ist eine Test-Mail.'
        try:
            send_mail(subject, body, None, [to])
            messages.success(request, 'E-Mail gesendet.')
        except Exception as e:
            messages.error(request, f'Fehler: {e}')
    return render(request, 'settingsmgr/smtp_test.html', {})
