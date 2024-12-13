from django.contrib import admin
from .models import Doctor, Patient

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'numero_licence','password', 'image')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'ramq','password', 'image', 'date_naissance', 'genre', 'ville_naissance', 'adresse', 'telephone')
