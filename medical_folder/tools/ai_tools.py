import random
from ..models import Doctor

def ai_scan(model, image):
    
    return "VGG16 - Image Classification", random.choice([True, False]), 'Just for testing porposes'

def suggest_doctor():
    return Doctor.objects.first()