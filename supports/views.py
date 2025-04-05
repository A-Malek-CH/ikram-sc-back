from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsPatient, IsAdmin

from backend import settings
from .models import SupportMessage, SupportMessageAnswer
from .serializers import SupportMessageSerializer, SupportMessageAnswerSerializer


class AskSupporMessagetView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = SupportMessageSerializer(data=request.data)
        if serializer.is_valid():
            support_message = serializer.save()
            return Response({**serializer.data, 'message': "Question has been created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            message = SupportMessage.objects.get(id=id)
        except SupportMessage.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        if message.user != request.user:
            return Response({'error': 'You do not have permission to delete this message'}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response({'message': 'Deleted successfully', 'id': id}, status=status.HTTP_200_OK)
    
class GetSupportMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            messages = SupportMessage.objects.all()
        else:
            messages = SupportMessage.objects.filter(user=request.user) | SupportMessage.objects.filter(is_private=False)

        serializer = SupportMessageSerializer(messages.distinct(), many=True)
        return Response(serializer.data)



class GetAnswerSupportMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        try:
            message = SupportMessage.objects.get(id=id)
        except SupportMessage.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        if message.user != request.user and message.is_private:
            return Response({'error': 'You do not have permission to view this message'}, status=status.HTTP_403_FORBIDDEN)
        answers = message.supportmessageanswer_set.all()
        serializer = SupportMessageAnswerSerializer(answers, many=True)
        return Response(serializer.data)


class AnswerSupportMessageView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = SupportMessageAnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({**serializer.data, 'message': 'Answer successfully created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            answer = SupportMessageAnswer.objects.get(id=id)
        except SupportMessageAnswer.DoesNotExist:
            return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)
        if answer.user != request.user:
            return Response({'error': 'You do not have permission to delete this answer'}, status=status.HTTP_403_FORBIDDEN)
        answer.delete()
        return Response({'message': 'Deleted successfully', 'id': id}, status=status.HTTP_200_OK)

    