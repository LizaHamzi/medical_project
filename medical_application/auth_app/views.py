from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import DoctorRegistrationForm
from .models import Doctor, Patient
from django.contrib.auth.hashers import check_password
import base64
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import DoctorRegistrationForm, PatientUpdateForm
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes 
from .serializers import DoctorSerializer, PatientSerializer
import urllib.parse
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from rest_framework import status
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient, Conversation, ChatSession, ChatMessage
from django.shortcuts import get_object_or_404, redirect, render
from .models import Patient, Conversation, ChatSession, ChatMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import re
from .models import ChatSession, ChatMessage


stripe.api_key = settings.STRIPE_SECRET_KEY



def homepage(request):
    return render(request, 'homepage.html')



FASTAPI_URL_FACE = 'http://127.0.0.1:8021/add-signature/'  
FASTAPI_URL_VOICE = 'http://127.0.0.1:8022/add-voice-signature/'

def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)  
            doctor.subscription = form.cleaned_data['subscription']

            # Redirigez vers une page de paiement Stripe
            subscription = form.cleaned_data['subscription']
            prices = {
                'basic': 2999,  # en cents
                'pro': 6999,
                'enterprise': 11999,
            }

            try:
                # Créez une session Stripe Checkout
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'CAD',
                            'product_data': {'name': f"{subscription.capitalize()} Subscription"},
                            'unit_amount': prices[subscription],
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri('/auth/success/'),
                    cancel_url=request.build_absolute_uri('/auth/cancel/'),
                )

                # Enregistrez le docteur après le paiement réussi
                doctor.save()
                messages.success(request, "Account created successfully! Please complete payment to activate your account.")
                return redirect(session.url)

            except Exception as e:
                print(f"Stripe error: {str(e)}")
                messages.error(request, "An error occurred during the payment process. Please try again.")
    else:
        form = DoctorRegistrationForm()

    return render(request, 'register.html', {'form': form})


def payment_success(request):
    messages.success(request, "Payment successful! Your account is now active.")
    return redirect('login')

def payment_cancel(request):
    messages.error(request, "Payment canceled. Please try again.")
    return redirect('register_doctor')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user_type = request.POST.get('user_type')  
        licence_number = request.POST.get('numero_licence')
        ramq_number = request.POST.get('ramq')

        if not user_type:
            messages.error(request, "Please select Doctor or Patient.")
            return redirect('login')  

        if user_type == 'doctor':
            try:
                doctor = Doctor.objects.get(email=email)
                if check_password(password, doctor.password):
                    if doctor.numero_licence == licence_number:
                        # Send email and user_type in the redirect URL
                        return redirect(f'/auth/face-id-capture/?email={email}&user_type={user_type}')
                    else:
                        messages.error(request, "Incorrect licence number for the doctor.")
                else:
                    messages.error(request, "Incorrect login credentials for the doctor.")
            except Doctor.DoesNotExist:
                messages.error(request, "Doctor not found. Please register first.")

        elif user_type == 'patient':
            try:
                patient = Patient.objects.get(email=email)
                if check_password(password, patient.password):
                    if patient.ramq == ramq_number:
                        # Send email and user_type in the redirect URL
                        return redirect(f'/auth/face-id-capture/?email={email}&user_type={user_type}')
                    else:
                        messages.error(request, "Incorrect RAMQ number for the patient.")
                else:
                    messages.error(request, "Incorrect login credentials for the patient.")
            except Patient.DoesNotExist:
                messages.error(request, "Patient not found. Please register first.")
        else:
            messages.error(request, "Please select Doctor or Patient.")

    return render(request, 'login.html')


def get_stored_image(request, email):
    try:
        # Fetch the doctor object based on the email
        doctor = Doctor.objects.get(email=email)
        if doctor.image:
            # Return the relative path to the image 
            return JsonResponse({"image_path": doctor.image.url}, status=200)
        else:
            return JsonResponse({"error": "No image found for this user"}, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

def list_doctors(request):
    # Récupérer tous les médecins depuis la base de données
    doctors = Doctor.objects.all()
    return render(request, 'list_doctors.html', {'doctors': doctors})


def face_id_capture(request):
    email = request.GET.get('email')
    user_type = request.GET.get('user_type')

    if not email or not user_type:
        error_message = "L'email ou le type d'utilisateur est manquant."
        return render(request, 'face_id_capture.html', {'error_message': error_message})

    context = {
        'email': email,
        'user_type': user_type  # Transmet user_type au template
    }

    return render(request, 'face_id_capture.html', context)


def voice_id_view(request):
    email = request.GET.get('email')  
    user_type = request.GET.get('user_type') 
    
    if not email or not user_type:
        
        error_message = "L'email ou le type d'utilisateur est manquant."
        return render(request, 'voice_id.html', {'error_message': error_message})

    # Passer les variables au template
    context = {
        'email': email,
        'user_type': user_type
    }
    return render(request, 'voice_id.html', context)



 

def verify_face_id(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user_type = request.POST.get('user_type') or request.GET.get('user_type')
        print(f"user type: {user_type}")
        face_image_file = request.FILES.get('face_image')
        if not email:
            return JsonResponse({"error": "L'email est manquant."}, status=400)

        if not user_type:
            return JsonResponse({"error": "Le type d'utilisateur est manquant."}, status=400)

        

        if not face_image_file:
            messages.error(request, "No image received.")
            return redirect('face_id_capture')

        try:
            # formData object 
            files = {'file': face_image_file}
            data = {'email': email}
            response = requests.post('http://127.0.0.1:8021/verify-face-id/', files=files, data=data)

            if response.status_code == 200:
                # Encode l'email avant de l'ajouter à l'URL
                encoded_email = urllib.parse.quote(email)
                if user_type == 'doctor':
                    # Rediriger avec l'email encodé dans l'URL
                    messages.success(request, "Face ID verified successfully.")
                    return redirect(f'http://127.0.0.1:8001/records/?email={encoded_email}')
                elif user_type == 'patient':
                    messages.success(request, "Vérification vocale réussie pour le patient.")
                    return redirect('profile_view', email=email)
                else:
                    messages.error(request, "Type d'utilisateur inconnu.")
                    return redirect('login')

            else:
                messages.error(request, "Face ID did not match.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Verification error: {e}")
            return redirect('login')

    return redirect('login')





@api_view(['GET'])
def get_doctor_by_email(request, email):
    decoded_email = urllib.parse.unquote(email)  
    print(f"Requête reçue pour l'email encodé : {email}")
    print(f"Email décodé : {decoded_email}")

    try:
        doctor = Doctor.objects.get(email=decoded_email)
        print(f"Docteur trouvé : {doctor}")
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)
    except Doctor.DoesNotExist:
        print(f"Docteur non trouvé pour l'email : {decoded_email}")
        return Response({'error': 'Doctor not found'}, status=404)


@api_view(['GET'])
def get_patients(request):
    patients = Patient.objects.all()
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_doctors(request):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_patient_by_id(request, id):
    try:
        patient = Patient.objects.get(id=id)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404)

@api_view(['GET'])
def get_doctor_by_id(request, id):
    try:
        doctor = Doctor.objects.get(id=id)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)
    except Doctor.DoesNotExist:
        return Response({'error': 'Doctor not found'}, status=404)
    

@api_view(['GET'])
def get_patient_by_email(request, email):
    try:
        patient = Patient.objects.get(email=email)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404)
    

@api_view(['PUT'])
def update_doctor(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    serializer = DoctorSerializer(doctor, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  
def create_patient(request):
    serializer = PatientSerializer(data=request.data)
    
    if serializer.is_valid():
        patient = serializer.save()
        return Response({'id': patient.id}, status=201)
    else:
        return Response(serializer.errors, status=400)
    



def profile_view(request, email):
    try:
        patient = get_object_or_404(Patient, email=email)
        print(f"email: {email}")
    except Patient.DoesNotExist:
        messages.error(request, "Patient introuvable.")
        return redirect('login')

    context = {
        'patient': patient
    }
    return render(request, 'profile.html', context)
    



def update_patient_profile(request, id):
    patient = get_object_or_404(Patient, id=id)

    if request.method == 'POST':
        form = PatientUpdateForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('profile_view', email=patient.email)
        else:
            messages.error(request, "Erreur lors de la mise à jour. Veuillez vérifier les informations.")
    else:
        form = PatientUpdateForm(instance=patient)

    return render(request, 'update_profile.html', {'form': form, 'patient': patient})


def view_medical_record(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    try:
        response = requests.get(f'http://localhost:8001/api/records/{patient_id}/')

        if response.status_code == 200:
            # Parse the API response
            record_data = response.json()
            print("Données du dossier médical :", record_data)  
            context = {'record': record_data, 'patient': patient}  
            return render(request, 'mondossier.html', context)
        else:
            print(f"Erreur {response.status_code} lors de la récupération du dossier médical.")
            messages.error(request, "Erreur lors de la récupération du dossier médical.")
            return redirect('profile_view', email=patient.email)

    except Exception as e:
        print(f"Exception occurred: {e}")  
        messages.error(request, f"Erreur : {e}")
        return redirect('profile_view', email=patient.email)


FASTAPI_VOICE_VERIFY_URL = 'http://127.0.0.1:8022/verify-voice-id/'

def verify_voice_id(request):
    if request.method == 'POST':
        email = request.POST.get('email') or request.GET.get('email')
        user_type = request.POST.get('user_type') or request.GET.get('user_type')
        
        print(f"user type: {user_type}")
        voice_file = request.FILES.get('voice_file')

        if not email:
            return JsonResponse({"error": "L'email est manquant."}, status=400)

        if not user_type:
            return JsonResponse({"error": "Le type d'utilisateur est manquant."}, status=400)

        if not voice_file:
            return JsonResponse({"error": "Aucun fichier audio envoyé."}, status=400)

        try:
            files = {'file': voice_file}
            data = {'email': email}

            response = requests.post(FASTAPI_VOICE_VERIFY_URL, files=files, data=data)
            print(f"Statut de la réponse FastAPI: {response.status_code}")
            print(f"Réponse FastAPI: {response.json()}")

            if response.status_code == 200:
        
                if user_type == 'doctor':
                    messages.success(request, "Vérification vocale réussie pour le docteur.")
                    return redirect(f'http://127.0.0.1:8001/records/?email={email}')
                elif user_type == 'patient':
                    messages.success(request, "Vérification vocale réussie pour le patient.")
                    return redirect('profile_view', email=email)
                else:
                    messages.error(request, "Type d'utilisateur inconnu.")
                    return redirect('login')

            else:
                messages.error(request, "La vérification vocale a échoué.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Erreur lors de la vérification vocale : {str(e)}")
            return redirect('login')

    return redirect('login')




def chatbot_page(request, email, conversation_id=None):
    # Récupérer le patient
    patient = get_object_or_404(Patient, email=email)

    # Vérifier si une nouvelle conversation doit être créée
    if 'new_conversation' in request.GET:
        # Crée une nouvelle conversation et session de chat
        conversation = Conversation.objects.create(email=email)
        chat_session = ChatSession.objects.create(conversation=conversation)
        # Redirige vers la nouvelle conversation
        return redirect('chat', email=email, conversation_id=conversation.id)

    # Charger la conversation spécifique ou la plus récente
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, email=email)
    else:
        conversation = Conversation.objects.filter(email=email).order_by('-created_at').first()
        if not conversation:
            # Crée une nouvelle conversation si aucune n'existe
            conversation = Conversation.objects.create(email=email)

    # Récupérer ou créer la session de chat la plus récente pour cette conversation
    chat_session = ChatSession.objects.filter(conversation=conversation).order_by('-created_at').first()
    if not chat_session:
        chat_session = ChatSession.objects.create(conversation=conversation)

    # Récupérer l'historique du chat et toutes les conversations pour l'utilisateur
    chat_history = ChatMessage.objects.filter(session__conversation=conversation).order_by('timestamp')
    conversations = Conversation.objects.filter(email=email).order_by('-created_at')

    context = {
        'patient': patient,
        'email': email,
        'chat_session': chat_session,
        'chat_history': chat_history,
        'conversations': conversations,
    }
    return render(request, 'chatbot.html', context)



@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        session_id = request.POST.get('session_id')

        if not email or not session_id:
            return JsonResponse({"error": "L'email ou l'ID de session est manquant."}, status=400)

        # Récupère la session de chat
        try:
            chat_session = ChatSession.objects.get(id=session_id, conversation__email=email)
        except ChatSession.DoesNotExist:
            return JsonResponse({"error": "Session de chat introuvable."}, status=404)

        user_input = request.POST.get('message')
        if not user_input:
            return JsonResponse({"error": "Le message est manquant."}, status=400)

        # Enregistre le message utilisateur
        ChatMessage.objects.create(session=chat_session, message=user_input, is_bot=False)

        try:
            # Ajoute un prompt spécifique pour guider Ollama
            medical_prompt = (
                "Tu es  un assistant médical. Répond uniquement aux questions liées à des sujets médicaux. "
                "Si la question n'est pas pertinente au domaine médical, répond : 'Désolé, je n'ai pas de réponse à cette question.'\n"
                f"Question : {user_input}"
            )

            # Exécute la commande pour obtenir une réponse dynamique
            result = subprocess.run(
                f'C:\\Users\\aziz\\AppData\\Local\\Programs\\Ollama\\ollama.exe run llama3.2 "{medical_prompt}"',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, encoding="utf-8"
            )

            response = result.stdout
            error = result.stderr

            if result.returncode != 0:
                print("Erreur lors de l'exécution du sous-processus:", error)
                return JsonResponse({"error": "Erreur lors de l'exécution du chatbot: " + error}, status=500)

            # Nettoyer la réponse de la console
            response_cleaned = re.sub(
                r"failed to get console mode for stdout: The handle is invalid\.\s*"
                r"failed to get console mode for stderr: The handle is invalid\.\s*", 
                "", response
            )

            if not response_cleaned.strip():
                return JsonResponse({"error": "La réponse du chatbot est vide."}, status=500)

            # Enregistre le message du bot dans l'historique
            ChatMessage.objects.create(session=chat_session, message=response_cleaned, is_bot=True)

            return JsonResponse({'response': response_cleaned}, status=200)

        except Exception as e:
            print("Exception lors de l'exécution de la commande:", str(e))
            return JsonResponse({"error": "Une erreur est survenue lors de l'exécution du chatbot."}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
