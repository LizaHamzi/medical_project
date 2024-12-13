from django import forms
from .models import Doctor, Patient
from django.core.exceptions import ValidationError

class DoctorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    SUBSCRIPTION_CHOICES = [
        ('basic', 'Basic - $29.99/month'),
        ('pro', 'Pro - $69.99/month'),
        ('enterprise', 'Enterprise - $119.99/month'),
    ]

    subscription = forms.ChoiceField(
        choices=SUBSCRIPTION_CHOICES,
        widget=forms.Select,  # Utilisez un menu déroulant
        label="Choose your subscription"
    )

    class Meta:
        model = Doctor
        fields = ['nom', 'prenom', 'email', 'password', 'numero_licence', 'image', 'voice_recording', 'subscription']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Doctor.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_numero_licence(self):
        numero_licence = self.cleaned_data.get('numero_licence')
        if Doctor.objects.filter(numero_licence=numero_licence).exists():
            raise ValidationError("This licence number is already in use.")
        return numero_licence

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise ValidationError("You must upload a profile image.")
        return image



class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'email', 'ramq', 'date_naissance',
            'genre', 'ville_naissance', 'adresse', 'telephone', 'image', 'voice_recording'
        ]
        widgets = {
            'date_naissance': forms.SelectDateWidget(years=range(1900, 2024)),
        }
