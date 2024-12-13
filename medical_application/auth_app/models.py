from django.db import models
from django.contrib.auth.hashers import make_password
import os

def upload_to(instance, filename):
    ext = filename.split('.')[-1]  # Extraire l'extension de l'image
    
    # Nettoyer l'email en remplaçant les caractères spéciaux
    safe_email = instance.email.replace('@', '_').replace('.', '_')
    
    # Renommer le fichier avec l'email nettoyé
    filename = f"{safe_email}.{ext}"  
    
    return os.path.join('image_doctors/', filename) 

# Fonction pour gérer le téléchargement des audios
def upload_to_voice_doctors(instance, filename):
    ext = filename.split('.')[-1]  # Extraire l'extension de l'image
    
    # Nettoyer l'email en remplaçant les caractères spéciaux
    safe_email = instance.email.replace('@', '_').replace('.', '_')
    
    # Renommer le fichier avec l'email nettoyé
    filename = f"{safe_email}.{ext}"  
    
    return os.path.join('doctor_voices/', filename) 

class Doctor(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    numero_licence = models.CharField(max_length=50)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True) 
    voice_recording = models.FileField(upload_to=upload_to_voice_doctors, blank=True, null=True)
    subscription = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_CHOICES,
        default='basic',
    )
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)  # Stocke l'ID client Stripe

    def save(self, *args, **kwargs):
        if not self.id and self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_licence}"
def upload_to_patients(instance, filename):
    ext = filename.split('.')[-1]  # Extraire l'extension de l'image
    
    # Nettoyer l'email en remplaçant les caractères spéciaux
    safe_email = instance.email.replace('@', '_').replace('.', '_')
    
    # Renommer le fichier avec l'email nettoyé
    filename = f"{safe_email}.{ext}"  
    
    return os.path.join('image_patients/', filename) 

# Fonction pour gérer le téléchargement des audios
def upload_to_voice_patients(instance, filename):
    ext = filename.split('.')[-1]  # Extraire l'extension de l'image
    
    # Nettoyer l'email en remplaçant les caractères spéciaux
    safe_email = instance.email.replace('@', '_').replace('.', '_')
    
    # Renommer le fichier avec l'email nettoyé
    filename = f"{safe_email}.{ext}"  
    
    return os.path.join('patient_voices/', filename) 




class Patient(models.Model):
    id = models.BigAutoField(primary_key=True)  
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    ramq = models.CharField(max_length=50)
    image = models.ImageField(upload_to=upload_to_patients, blank=True, null=True)
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    genre = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')], null=True, blank=True)
    ville_naissance = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ville de naissance")
    adresse = models.TextField(null=True, blank=True, verbose_name="Adresse maison")
    telephone = models.CharField(max_length=15, null=True, blank=True)
    voice_recording = models.FileField(upload_to=upload_to_voice_patients, blank=True, null=True)  

    def save(self, *args, **kwargs):
        # Hacher le mot de passe uniquement si c'est un nouvel enregistrement
        if not self.id and self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.ramq}"
    

class Conversation(models.Model):
    email = models.EmailField()  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Conversation for {self.email} at {self.created_at}"

class ChatSession(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='sessions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat session in conversation {self.conversation.id} at {self.created_at}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True)
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "Bot" if self.is_bot else "User"
        return f"{sender}: {self.message[:50]}"
