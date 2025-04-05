import os
from django.db import models
from appointments.models import Appointment
from users.models import User


class MedicalRecord(models.Model):
    def get_upload_to(self, filename):
        return os.path.join('images', 'medical_records', str(self.pk), filename)
    type = models.CharField(max_length=50, choices=Appointment.APPOINTMENT_TYPES)
    image = models.ImageField(upload_to=get_upload_to)
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_uploaded = models.BooleanField(default=False)
    appointment = models.ForeignKey(on_delete=models.CASCADE, to=Appointment, null=True, blank=True)
    uploader = models.ForeignKey(on_delete=models.CASCADE, to=User, null=True, blank=True)
    
    @property
    def user(self):
        if self.is_uploaded:
            return self.uploader
        return self.appointment.user
    
    
    def __str__(self):
        return self.type
    
class AiScan(models.Model):
    model = models.CharField(max_length=50)
    result = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    medical_record = models.ForeignKey(on_delete=models.CASCADE, to=MedicalRecord)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model

class Doctor(models.Model):
    SPECIALTY_CHOICES = [('cardiology', 'Cardiology'),
                        ('neurology', 'Neurology'),
                        ('orthopedics', 'Orthopedics'),
                        ('pediatrics', 'Pediatrics'),
                        ('dermatology', 'Dermatology')]
    name = models.CharField(max_length=50)
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class MedicalSuggestion(models.Model):
    model = models.CharField(max_length=50)
    ai_scan = models.ForeignKey(on_delete=models.CASCADE, to=AiScan)
    doctor = models.ForeignKey(on_delete=models.CASCADE, to=Doctor)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model




