from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsPatient, IsAdmin
from .models import Appointment
from .serializers import AppointmentSerializer

# Patient Views
class PatientAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    
    def post(self, request):
        request.data['user'] = request.user.id
        if not request.data.get('email'):
            request.data['email'] = request.user.email
        
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({**serializer.data, "message": "Appointment demand has been created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment = Appointment.objects.filter(id=id).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        if appointment.user != request.user:
            return Response({'error': 'You do not have permission to delete this appointment'}, status=status.HTTP_403_FORBIDDEN)
        if appointment.state == 'P':
            appointment.delete()
            return Response({'message': 'Appointment deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Cannot delete an appointment that is not pending'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        appointments = Appointment.objects.filter(user=request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    
    def post(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        appointment = Appointment.objects.filter(id=id).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        if appointment.user != request.user:
            return Response({'error': 'You do not have permission to cancel this appointment'}, status=status.HTTP_403_FORBIDDEN)
        if appointment.state == 'A':
            appointment.state = 'C'
            appointment.save()
            return Response({'message': 'Appointment canceled successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Cannot cancel an appointment that is not accepted'}, status=status.HTTP_400_BAD_REQUEST)

class FilteredAppointmentsView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        appointment_type = request.query_params.get('type')
        
        filters = {}
        if start_date and end_date:
            filters['appointment_date__range'] = [start_date, end_date]
        if appointment_type:
            filters['type'] = appointment_type
        
        appointments = Appointment.objects.filter(**filters).values('state', 'creation_date', 'appointment_date')
        return Response(appointments, status=status.HTTP_200_OK)



# Admin Views
class WalkInAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):
        request.data['is_walk_in'] = True
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({**serializer.data, "message": "Appointment demand has been created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageAppointmentDemandsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        appointment = Appointment.objects.filter(id=id).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        if appointment.state == 'P':
            appointment.state = 'A'
            appointment.save()
            return Response({'message': 'Appointment demand accepted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Only pending appointments can be accepted'}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        appointment = Appointment.objects.filter(id=id).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        if appointment.state == 'P':
            appointment.state = 'R'
            appointment.save()
            return Response({'message': 'Appointment demand rejected successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Only pending appointments can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        appointment_type = request.query_params.get('type')
        
        filters = {}
        if start_date and end_date:
            filters['appointment_date__range'] = [start_date, end_date]
        if appointment_type:
            filters['type'] = appointment_type
        
        appointments = Appointment.objects.filter(**filters)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FinishAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        appointment = Appointment.objects.filter(id=id).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        if appointment.state == 'A':
            appointment.state = 'F'
            appointment.attendance_date = now()
            appointment.save()
            return Response({'message': 'Appointment marked as finished'}, status=status.HTTP_200_OK)
        return Response({'error': 'Only accepted appointments can be marked as finished'}, status=status.HTTP_400_BAD_REQUEST)

class MarkMissedAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Appointment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        appointment = Appointment.objects.filter(id=id).first()
        if not appointment:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        if appointment.state == 'A':
            appointment.state = 'M'
            appointment.save()
            return Response({'message': 'Appointment marked as missed'}, status=status.HTTP_200_OK)
        return Response({'error': 'Only accepted appointments can be marked as missed'}, status=status.HTTP_400_BAD_REQUEST)    