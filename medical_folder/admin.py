from django.contrib import admin
from .models import MedicalRecord, AiScan, Doctor, MedicalSuggestion

admin.site.register(MedicalRecord)
admin.site.register(AiScan)
admin.site.register(Doctor)
admin.site.register(MedicalSuggestion)
