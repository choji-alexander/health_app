from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('health_worker_registration/', views.health_worker_registration, name='health_worker_registration'),
    path('patient_registration/', views.patient_registration, name='patient_registration'),
    path('registration_success/', views.registration_success, name='registration_success'),
    path('create_medical_record/', views.create_medical_record, name='create_medical_record'),
    path('statistics/', views.display_statistics, name='statistics'),
    path('user_medical_records/', views.list_users_and_medical_records, name='user_medical_records'),
    path('filter_users/', views.filter_users, name='filter_users'),
    path('search_and_book_appointment/', views.search_and_book_appointment, name='search_and_book_appointment'),
    path('manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('access_denied/', views.access_denied, name='access_denied'),
    path('health_worker_dashboard/', views.health_worker_dashboard, name='health_worker_dashboard'),

    # path('appointment_confirmation/', views.appointment_confirmation, name='appointment_confirmation'),

    # Other URL patterns...
]
