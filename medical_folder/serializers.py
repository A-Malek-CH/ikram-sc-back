from rest_framework import serializers
from .models import MedicalRecord, AiScan, Doctor, MedicalSuggestion

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

class AiScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiScan
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class MedicalSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalSuggestion
        fields = '__all__'