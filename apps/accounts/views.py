from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, ProfileForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registrierung erfolgreich. Ein Admin muss deinen Zugang freigeben.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    prof = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil gespeichert.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=prof)
        # E-Mail nur anzeigen
        form.fields['email_readonly'].initial = request.user.email

    return render(request, 'accounts/profile.html', {'form': form})
