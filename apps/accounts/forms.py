from django import forms
from django.contrib.auth.models import User
from .models import Profile
from apps.iam.models import Function

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Diese E-Mail ist bereits registriert.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].lower()
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    email_readonly = forms.EmailField(label="E-Mail (Login)", required=False, disabled=True)
    # Dropdowns für Funktionen
    function_1 = forms.ModelChoiceField(label="1. Funktion im Verband", queryset=Function.objects.all(), required=False)
    function_2 = forms.ModelChoiceField(label="2. Funktion im Verband", queryset=Function.objects.all(), required=False)
    function_3 = forms.ModelChoiceField(label="3. Funktion im Verband", queryset=Function.objects.all(), required=False)
    function_4 = forms.ModelChoiceField(label="4. Funktion im Verband", queryset=Function.objects.all(), required=False)
    function_5 = forms.ModelChoiceField(label="5. Funktion im Verband", queryset=Function.objects.all(), required=False)

    class Meta:
        model = Profile
        fields = [
            'first_name','last_name',
            'street','house_no','zip_code','city','phone',
            'account_holder','iban','bic','bank_name',
            'signature_image',
            'function_1','function_2','function_3','function_4','function_5',
        ]
        widgets = {
            'signature_image': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }
