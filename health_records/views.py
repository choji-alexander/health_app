from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import HealthWorkerRegistrationForm, PatientRegistrationForm
from django.contrib.auth.decorators import login_required
from .forms import MedicalRecordForm, CustomAuthenticationForm
from .models import User, MedicalRecord
from django.db.models import Count
import matplotlib.pyplot as plt
from .forms import MedicalRecordFilterForm
from django.core.mail import send_mail
from .forms import AppointmentForm, EmailNotificationForm
from .models import Appointment
from .forms import AcceptRejectAppointmentForm
from django.contrib.auth.decorators import user_passes_test
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')


# @user_passes_test(lambda u: u.is_health_worker(), login_url='access_denied')
# class UserMedicalRecordListView(ListView):
    # model = User
    # template_name = 'user_medical_records.html'
    # context_object_name = 'users'


# def user_registration(request):
    # if request.method == 'POST':
        # form = UserRegistrationForm(request.POST)
        # if form.is_valid():
            # user = form.save()
            # Redirect to the registration success page
            # return redirect('registration_success')
    # else:
        # form = UserRegistrationForm()
    # return render(request, 'registration_form.html', {'form': form})


def login_view(request):
    if request.method == 'POST' and request.is_healthcare_worker:
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('health_worker_dashboard')

    elif request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('search_and_book_appointment')

    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


def health_worker_registration(request):
    if request.method == 'POST':
        form = HealthWorkerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_healthcare_worker = True  # Set the user as a health worker
            user.save()
            login(request, user)
        return redirect('registration_success')
    else:
        form = HealthWorkerRegistrationForm()

    return render(request, 'registration_form.html', {'form': form})


def patient_registration(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_healthcare_worker = False  # Set the user as a health worker
            user.save()
            login(request, user)
            return redirect('registration_success')
    else:
        form = PatientRegistrationForm()

    return render(request, 'registration_form.html', {'form': form})


def registration_success(request):
    return render(request, 'registration_success.html')


def create_medical_record(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.user = request.user  # Associate the record with the logged-in user
            medical_record.save()
            return redirect('user_profile')  # Redirect to the user's profile or other appropriate page
    else:
        form = MedicalRecordForm()

    return render(request, 'medical_record_form.html', {'form': form})


@user_passes_test(lambda u: u.is_health_worker(), login_url='access_denied')
def display_statistics(request):
    # Query the database to get the count of users for each disease
    disease_counts = MedicalRecord.objects.values('disease').annotate(count=Count('user'))

    # Extract disease names and counts from the query results
    diseases = [record['disease'] for record in disease_counts]
    user_counts = [record['count'] for record in disease_counts]

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(diseases, user_counts)
    plt.xlabel('Disease')
    plt.ylabel('User Count')
    plt.title('User Count by Disease')

    # Save the chart as an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.read()).decode()
    buffer.close()

    plt.close()

    return render(request, 'statistics.html', {'chart_image': chart_image})


@user_passes_test(lambda u: u.is_health8_worker(), login_url='access_denied')
def list_users_and_medical_records(request):
    # Retrieve the list of users and their medical records
    users_with_medical_records = User.objects.filter(is_health_worker=False)
    return render(request, 'user_medical_records.html', {'users_with_medical_records': users_with_medical_records})


@user_passes_test(lambda u: u.is_health_worker(), login_url='access_denied')
def filter_users(request):
    users = User.objects.all()  # Start with all users

    if request.method == 'POST':
        form = MedicalRecordFilterForm(request.POST)
        if form.is_valid():
            disease = form.cleaned_data.get('disease')
            if disease:
                users = users.filter(medicalrecord__disease__icontains=disease)

    else:
        form = MedicalRecordFilterForm()

    return render(request, 'user_filter.html', {'form': form, 'users': users})


def search_and_book_appointment(request):
    if request.method == 'POST':
        appointment_form = AppointmentForm(request.POST)
        email_form = EmailNotificationForm(request.POST)

        if appointment_form.is_valid() and email_form.is_valid():
            health_worker = appointment_form.cleaned_data['health_worker']
            date_time = appointment_form.cleaned_data['date_time']
            subject = email_form.cleaned_data['subject']
            message = email_form.cleaned_data['message']

            appointment = Appointment(
                health_worker=health_worker,
                patient=request.user,  # Assuming the logged-in user is the patient
                date_time=date_time,
            )
            appointment.save()

            # Send an email notification to the health worker
            send_mail(subject, message, 'your_email@example.com', [health_worker.email])

            return redirect('appointment_confirmation')

    else:
        appointment_form = AppointmentForm()
        email_form = EmailNotificationForm()

    return render(request, 'search_and_book_appointment.html', {
        'appointment_form': appointment_form,
        'email_form': email_form,
        'health_workers': User.objects.filter(is_healthcare_worker=True)
    })


@user_passes_test(lambda u: u.is_health_worker(), login_url='access_denied')
def manage_appointments(request):
    health_worker = request.user
    appointments = Appointment.objects.filter(health_worker=health_worker)

    if request.method == 'POST':
        form = AcceptRejectAppointmentForm(request.POST)
        if form.is_valid():
            appointment_id = form.cleaned_data['appointment_id']
            action = form.cleaned_data['action']

            appointment = appointments.get(pk=appointment_id)
            if action == 'accept':
                appointment.accepted = True
                appointment.save()
            elif action == 'reject':
                appointment.accepted = False
                appointment.save()

    else:
        form = AcceptRejectAppointmentForm()

    return render(request, 'manage_appointments.html', {
        'appointments': appointments,
        'form': form,
    })


@login_required
def health_worker_dashboard(request):
    # Retrieve appointments for the logged-in health worker
    appointments = Appointment.objects.filter(health_worker=request.user, accepted=True)

    # Gather statistics
    appointment_count_by_disease = {}
    for appointment in appointments:
        medical_record = MedicalRecord.objects.filter(patient=appointment.patient).first()
        if medical_record:
            disease = medical_record.disease
            if disease in appointment_count_by_disease:
                appointment_count_by_disease[disease] += 1
            else:
                appointment_count_by_disease[disease] = 1

    return render(request, 'health_worker_dashboard.html', {
        'appointments': appointments,
        'statistics': appointment_count_by_disease,
    })


def access_denied(request):
    return render(request, 'access_denied.html')
