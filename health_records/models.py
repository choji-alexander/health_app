from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_healthcare_worker = models.BooleanField(default=False)

    def is_health_worker(self):
        return self.is_authenticated and self.is_healthcare_worker

    def __str__(self):
        return self.email


class MedicalRecord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    disease = models.CharField(max_length=100)
    symptoms = models.TextField()
    diagnosis = models.TextField()
    prescription = models.TextField()
    date_of_record = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Medical Record for {self.user.email}"


class Appointment(models.Model):
    health_worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_received')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_made')
    date_time = models.DateTimeField()
    accepted = models.BooleanField(default=False)
