import os
from django.db import models
from appointments.models import Appointment


class MedicalRecord(models.Model):
    def get_upload_to(self, filename):
        return os.path.join('images', 'medical_records', str(self.pk), filename)
    type = models.CharField(max_length=50, choices=Appointment.APPOINTMENT_TYPES)
    image = models.ImageField(upload_to=get_upload_to)
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    appointment = models.ForeignKey(on_delete=models.CASCADE, to=Appointment)
    
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
    name = models.CharField(max_length=50)
    specialty = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
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




