from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import MedicalRecord, User


class HealthWorkerRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'is_healthcare_worker', 'password']


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['disease', 'symptoms', 'diagnosis', 'prescription']
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 3}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'prescription': forms.Textarea(attrs={'rows': 3})
        }


class AppointmentForm(forms.Form):
    health_worker = forms.ModelChoiceField(queryset=User.objects.filter(is_healthcare_worker=True))
    date_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))


class EmailNotificationForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class MedicalRecordFilterForm(forms.Form):
    disease = forms.CharField(required=False)


class AcceptRejectAppointmentForm(forms.Form):
    APPOINTMENT_ACTIONS = [
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ]

    appointment_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.ChoiceField(choices=APPOINTMENT_ACTIONS, widget=forms.RadioSelect())


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the username field
        del self.fields['username']

    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
