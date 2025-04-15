from rest_framework.views import APIView, Response
from django.db.models import Q

from appointments.models import Appointment
from users.models import Notification
from .serializers import AiScanSerializer, DoctorSerializer, MedicalSuggestionSerializer, RecordSerializer
from .models import AiScan, Doctor, MedicalRecord
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsPatient, IsPremuim
from users.authentication import JSONWebTokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from django.http import HttpResponse
from users.custom_renderers import ImageRenderer
from users.permissions import IsAdmin
from backend.settings import AI_SCAN_MODELS

from medical_folder.tools.ai_tools import ai_scan, suggest_doctor

class CreateRecordView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        data = dict(request.data)
        if 'image' not in data:
            return Response({'error': 'Image is required'}, status=400)
        if 'appointment' not in data:
            return Response({'error': 'Appointment ID is required'}, status=400)
        if 'description' not in data:
            return Response({'error': 'Description is required'}, status=400)
        if 'type' not in data:
            return Response({'error': 'Type is required'}, status=400)
        
        record_data = dict(type = data['type'][0], image = data['image'][0], appointment = data['appointment'][0], description = data['description'][0])
        
        appointment = Appointment.objects.filter(id=record_data['appointment']).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=404)
        if appointment.state != 'F':
            return Response({'error': 'Appointment must be finished'}, status=400)
        serializer = RecordSerializer(data=record_data)
        if serializer.is_valid():
            serializer.save()
            appointment.state = 'D'
            appointment.save() 
            if not appointment.is_walk_in:
                Notification.objects.create(
                    user=appointment.user,
                    description=f'Your medical result has been uploaded.',
                    type='message'
                )
            return Response(data={**serializer.data, "message": "Medical record has been created successfully"}, status=200)
        return Response(data=serializer.errors, status=500)
    
class GetRecordImageView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    renderers_classes = [ImageRenderer]
    def get(self, request, id):
        medica_record = MedicalRecord.objects.filter(id=id).first()
        if not medica_record:
            return Response({'error': 'Medical record not found'}, status=404)
        if medica_record.appointment.user.id != request.user.id and request.user.role != 'admin':
            return Response({'error': 'You are not authorized to view this medical record'}, status=403)
        data = medica_record.image
        return HttpResponse(data, content_type='image/' + data.path.split(".")[-1])

class GetRecordView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        records = MedicalRecord.objects.filter(
        Q(appointment__user=request.user) |
        Q(uploader=request.user, is_uploaded=True)).all()
        serializer = RecordSerializer(instance=records, many=True)
        return Response(data=serializer.data)
    

class AiScanView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    def post(self, request):
        model = request.data.get('model')
        if not model:
            return Response({'error': 'Model is required'}, status=400)
        if model not in AI_SCAN_MODELS:
            return Response({'error': 'Invalid model'}, status=400)
        medical_record = request.data.get('medical_record')
        if not medical_record:
            return Response({'error': 'Medical record is required'}, status=400)
        try:
            image = MedicalRecord.objects.filter(id=medical_record).first().image
        except:
            return Response({'error': 'Medical record not found'}, status=404)
        model, result, description = ai_scan(model, image)
        serializer = AiScanSerializer(data=dict(model=model, result=result, description=description, medical_record=medical_record))
        if serializer.is_valid():
            serializer.save()
            return Response(data={**serializer.data, "message": "AI has scaned your medical record"}, status=200)
        return Response(data=serializer.errors, status=500)
    
    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'can\'t delete without id'})
        instance = AiScan.objects.filter(id=id).first()
        if not instance:
            return Response({'error': 'there are no element with such id'})
        if (instance.medical_record.user.id == request.user.id) or request.user.role == 'admin':
            instance.delete()
            return Response({'id': id, "message": "AI Scan has been deleted successfully"}, status=200)
        else:
            return Response({'error': 'non authorized'})
    
    
    # Add AI scan to medical record getting
    def get(self, request):
        scans = AiScan.objects.filter(
        Q(medical_record__appointment__user=request.user) |
        Q(medical_record__uploader=request.user, medical_record__is_uploaded=True)).all()
        serializer = AiScanSerializer(instance=scans, many=True)
        return Response(data=serializer.data)


class ManageDoctorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(instance=doctors, many=True)
        return Response(data=serializer.data)
    
    def post(self, request):
        serialzer = DoctorSerializer(data=request.data)
        if serialzer.is_valid():
            serialzer.save()
            return Response(data={**serialzer.data, "message": "Doctor has been added successfully"}, status=200)
        print(serialzer.errors)
        return Response(data=serialzer.errors, status=500)
    
    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'can\'t delete without id'})
        instance = Doctor.objects.filter(id=id).first()
        if not instance:
            return Response({'error': 'there are no element with such id'})
        instance.delete()
        return Response({'id': id, "message": "Doctor has been deleted successfully"}, status=200)
    
    def put(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'can\'t update without id'})
        instance = Doctor.objects.filter(id=id).first()
        if not instance:
            return Response({'error': 'there are no element with such id'})
        serializer = DoctorSerializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={**serializer.data, "message":"Doctor has been updated successfully"}, status=200)
        return Response(data=serializer.errors, status=500)



class CreateUploadedRecordView(APIView):
    permission_classes = [IsAuthenticated, IsPatient, IsPremuim]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        print(request.data)
        data = dict(request.data)
        if 'image' not in data:
            return Response({'error': 'Image is required'}, status=400)
        if 'type' not in data:
            return Response({'error': 'Type is required'}, status=400)
        
        record_data = dict(type = data['type'][0], image = data['image'][0], uploader = request.user.id, is_uploaded = True)
        
        serializer = RecordSerializer(data=record_data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={**serializer.data, "message": "Medical record has been created successfully"}, status=200)
        return Response(data=serializer.errors, status=500)

class DoctorSuggestionView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    def post(self, request):
        doctor = suggest_doctor()
        data = dict(model = "Doctor Suggestor - 10", ai_scan = request.data.get('ai_scan'), doctor = doctor.id)
        serializer = MedicalSuggestionSerializer(instance=doctor)
        if not serializer.is_valid():
            return Response({'error': 'Doctor not found'}, status=404)
        serializer.save()
        return Response(data={**serializer.data, "message": "Doctor has been suggested successfully"}, status=200)
