from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from django.http import HttpResponse
from django.conf import settings
from rest_framework import parsers, renderers, status
from .serializers import AuthTokenSerializer
from .serializers import UserSerializer, ProfileSerializer, ProfilePictureSerializer, NotificationSerializer, UserVerificationRecordSerializer
import jwt, datetime
from .models import User, VerificationCode, Notification
import random
from django.core.mail import send_mail
from .custom_renderers import ImageRenderer
from rest_framework import generics
from .models import Profile

class Login(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = jwt.encode({
                'email': serializer.validated_data['email'],
                'iat': datetime.datetime.utcnow(),
                'nbf': datetime.datetime.utcnow() + datetime.timedelta(minutes=-5),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5)
            }, settings.SECRET_KEY, algorithm='HS256')
            user = User.objects.filter(email=serializer.validated_data['email']).first()
            return Response({'token': token, 'role': user.role})
        user = User.objects.filter(email=request.data['email']).first()
        if user:
            if not user.is_active:
                return Response({'error': 'You need to verify your email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignupView(APIView): 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
        code = ''.join([str(random.choice(range(10))) for i in range(5)])
        verificationCode = VerificationCode(code=code, user=instance)
        verificationCode.save()
        data = serializer.validated_data
        subject = f'welcome to {settings.APP_NAME}'
        message = f'Hi {data["first_name"]} {data["last_name"]} , thank you for registering in {settings.APP_NAME}, your verification code is: {code}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (data['email'],)
        send_mail( subject, message, email_from, recipient_list )
        return Response({'email': data['email'], "message": 'A verification code has been sent to your email'}, status=200)

class ResendVerificationCode(APIView): 
    def post(self, request):
        user = User.objects.filter(email=request.data.get('email')).first()
        if not user:
            return Response({'error': 'There is no user with such email'}, status=400)
        if user.is_active:
            return Response({'error': 'The Email is already verified'}, status=400)
        old_verification_code = VerificationCode.objects.filter(user=user)
        for code in old_verification_code:
            code.delete()
        code = ''.join([str(random.choice(range(10))) for i in range(5)])
        verificationCode = VerificationCode(code=code, user=user)
        verificationCode.save()
        subject = 'welcome to HomeCare'
        message = f'Hi {user.first_name} {user.last_name} , thank you for registering in HomeCare, your verification code is: {code}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (user.email,)
        send_mail( subject, message, email_from, recipient_list )
        return Response({'email': user.email})

class SignupVerificationView(APIView):  
    def post(self, request):
        code = request.data['code'] 
        user = User.objects.filter(email=request.data['email']).first()
        user_code = VerificationCode.objects.filter(user=user.id).first()   
        if code == user_code.code:
            user_code.delete()
            user.is_active = True
            Profile(user=user).save()
            user.save()
            return Response({'email': user.email, 'message': 'Your email has been verified'}, status=200)
        return Response({'error': 'Can\'t verify user'}, status=400)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        user_data = UserSerializer(instance=user).data
        profile_data = ProfileSerializer(instance=user.profile).data
        user_data.pop('password')
        profile_data.pop('id')
        profile_data.pop('user')
        data = dict(**(user_data), **(profile_data))
        return Response(data=data)
    
class ChangeProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]
    
    def post(self, request):
        user = request.user
        serializer = ProfilePictureSerializer(instance=user, data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Profile picture changed successfully'}, status=200)
        return Response(data=serializer.errors, status=400)

class OtherProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        user = User.objects.filter(id=id).first()
        user_data = UserSerializer(instance=user).data
        profile_data = ProfileSerializer(instance=user.profile).data
        profile_data.pop('id')
        profile_data.pop('user')
        data = dict(**(user_data), **(profile_data))
        return Response(data=data)

class FetchProfilePictureView(generics.RetrieveAPIView):
    renderers_classes = [ImageRenderer]
    def get(self, request, id):
        queryset = User.objects.get(id=id).picture
        data = queryset
        return HttpResponse(data, content_type='image/' + data.path.split(".")[-1])
    
class ResetPassword(APIView): 
    def post(self, request):
        request.data['email'] = request.user.email
        serializer = UserSerializer(instance=request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
        data = serializer.validated_data
        subject = 'welcome to HomeCare'
        message = f'Hi {request.user.first_name} {request.user.last_name} , your password has been changed.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (request.user.email,)
        send_mail( subject, message, email_from, recipient_list )
        return Response({'email': request.user.email})

class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-creation_date')
        serializer = NotificationSerializer(instance=notifications, many=True)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return Response(data=serializer.data)

    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'error': 'Notification ID is required'}, status=400)
        notification = Notification.objects.filter(id=id).first()
        if not notification:
            return Response({'error': 'Notification not found'}, status=400)
        if notification.user != request.user:
            return Response({'error': 'You do not have permission to delete this notification'}, status=403)
        notification.delete()
        return Response({'message': 'Notification deleted successfully'}, status=200)
