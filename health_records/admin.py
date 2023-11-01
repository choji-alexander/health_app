from django.contrib import admin
from .models import User, Appointment, MedicalRecord

admin.site.register(User)
admin.site.register(MedicalRecord)
admin.site.register(Appointment)
