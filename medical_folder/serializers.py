from rest_framework import serializers
from .models import MedicalRecord

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'