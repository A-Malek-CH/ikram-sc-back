from rest_framework import serializers
from .models import SupportMessage, SupportMessageAnswer

class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = '__all__'

class SupportMessageAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessageAnswer
        fields = '__all__'