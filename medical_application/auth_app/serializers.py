# serializers.py
from rest_framework import serializers
from .models import Doctor, Patient

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'nom', 'prenom', 'email', 'numero_licence','image', 'subscription']  

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'email', 'ramq', 'password', 'image', 'date_naissance', 'genre', 'ville_naissance', 'adresse', 'telephone', 'voice_recording']  