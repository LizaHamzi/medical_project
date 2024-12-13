from django.urls import path
from .views import login_view,register_doctor,list_doctors, face_id_capture, verify_face_id, get_stored_image
from django.conf import settings
from django.conf.urls.static import static
from auth_app.views import get_doctor_by_id, get_doctors, get_patient_by_id, get_patients, get_doctor_by_email, get_patient_by_email, create_patient, profile_view, update_patient_profile, view_medical_record, voice_id_view, verify_voice_id, chatbot_view, chatbot_page, update_doctor, payment_success, payment_cancel

urlpatterns = [
    
    path('register/',register_doctor, name='register_doctor'),
    path('login/', login_view, name='login'), 
    path('doctors/',list_doctors, name='list_doctors'),
    path('get-image/<str:email>/', get_stored_image, name='get_stored_image'),
    path('face-id-capture/', face_id_capture, name='face_id_capture'),
    path('verify_voice_id/', verify_voice_id, name='verify_voice_id'),
    path('voice-id/', voice_id_view, name='voice_id'),
    path('verify-face-id/', verify_face_id, name='verify_face_id'), 
    path('api/patients/', get_patients, name='get_patients'),
    path('api/doctors/', get_doctors, name='get_doctors'),
    path('api/patients/<int:id>/', get_patient_by_id, name='get_patient_by_id'),
    path('api/doctors/<int:id>/', get_doctor_by_id, name='get_doctor_by_id'), 
    path('api/doctor/<str:email>/', get_doctor_by_email, name='get_doctor_by_email'),
    path('api/patient/<str:email>/', get_patient_by_email, name='get_patient_by_email'),
    path('api/patients/create', create_patient, name='create_patient'),
    path('profile/<str:email>/', profile_view, name='profile_view'),
    path('profile/update/<int:id>/', update_patient_profile, name='update_patient_profile'),
    path('profile/dossier/<int:patient_id>/', view_medical_record, name='view_medical_record'),
    path('chatbot/', chatbot_view, name='chatbot'),
    path('chat/<str:email>/', chatbot_page, name='chat'),
    path('chat/<str:email>/<int:conversation_id>/', chatbot_page, name='chat'),
    path('api/doctors/<int:doctor_id>/update/', update_doctor, name='update_doctor'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),



]

