from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from django.http import HttpResponse
from django.conf import settings
from rest_framework import parsers, renderers, status

from appointments.models import Appointment
from medical_folder.models import Doctor
from users.permissions import IsAdmin, IsPatient
from .serializers import AuthTokenSerializer, SettingSerializer
from .serializers import UserSerializer, ProfileSerializer, ProfilePictureSerializer, NotificationSerializer
import jwt, datetime
from .models import Settings, User, VerificationCode, Notification
import random
from django.core.mail import send_mail
from .custom_renderers import ImageRenderer
from rest_framework import generics
from .models import Profile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password



class Login(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request):
        print(request.data)
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
        html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Hi <strong>{data["first_name"]} {data["last_name"]}</strong>,</p>
        <p>Thank you for registering in <strong>{settings.APP_NAME}</strong>!</p>
        <p>Your verification code is:</p>
        <div style="font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px 0;">
          {code}
        </div>
        <p>Please enter this code to verify your email address.</p>
        <br>
        <p style="font-size: 12px; color: gray;">If you didn’t request this, you can ignore this email.</p>
      </body>
    </html>
    """

        send_mail( subject, message, email_from, recipient_list, html_message=html_message, fail_silently=False)
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
        html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Hi <strong>{user.first_name} {user.last_name}</strong>,</p>
        <p>Thank you for registering in <strong>{settings.APP_NAME}</strong>!</p>
        <p>Your verification code is:</p>
        <div style="font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px 0;">
          {code}
        </div>
        <p>Please enter this code to verify your email address.</p>
        <br>
        <p style="font-size: 12px; color: gray;">If you didn’t request this, you can ignore this email.</p>
      </body>
    </html>
    """

        send_mail( subject, message, email_from, recipient_list, html_message=html_message, fail_silently=False)
        return Response({'email': user.email, "message": 'A verification code has been sent to your email'}, status=200)

class SignupVerificationView(APIView):  
    def post(self, request):
        code = request.data['code'] 
        user = User.objects.filter(email=request.data['email']).first()
        user_code = VerificationCode.objects.filter(user=user.id).first()   
        if code == user_code.code:
            user_code.delete()
            user.is_active = True
            Profile(user=user).save()
            Settings(user=user).save()
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
        data = dict(**(user_data), **(profile_data), is_premium=user.is_premium)
        return Response(data=data)
    
class ChangeProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]
    
    def post(self, request):
        user = request.user
        serializer = ProfilePictureSerializer(instance=user, data=request.data)
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
        user_data.pop('password')
        data = dict(**(user_data), **(profile_data))
        return Response(data=data)

class FetchProfilePictureView(generics.RetrieveAPIView):
    renderers_classes = [ImageRenderer]
    def get(self, request, id):
        data = User.objects.get(id=id).picture
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

class NotificationsCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        count = notifications.count()
        return Response({'count': count})

class UpgradeToPremiumView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    def post(self, request):
        user = request.user
        if user.is_premium:
            return Response({'error': 'You are already a premium user'}, status=400)
        user.is_premium = True
        user.save()
        return Response({'message': 'You are now a premium user'}, status=200)
    
    
class StatisticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request):
            return Response({
  "total_patients": User.objects.filter(role='patient').count(),
  "total_appointments": Appointment.objects.all().count(),
  "total_doctors": Doctor.objects.all().count(),
  "pending_appointments": Appointment.objects.filter(state='F').count(),
  "today_appointments": Appointment.objects.filter(state='P').count(),
  "completion_rate": (Appointment.objects.filter(appointment_date__date=timezone.localdate()).filter(state__in=['F', 'M', 'D']).count() / Appointment.objects.filter(appointment_date__date=timezone.localdate()).filter(state__in=['A', 'F', 'M', 'C', 'D']).count() if Appointment.objects.filter(appointment_date__date=timezone.localdate()).filter(state__in=['A', 'F', 'M', 'C', 'D']).count() > 0 else 0) * 100
,
  "avg_tests_per_day": 24.3,
  "patient_satisfaction": 4.8,
  "monthly_appointments": [
    {"name": "Jan", "value": 65},
    {"name": "Feb", "value": 72},
    {"name": "Mar", "value": 85},
    {"name": "Apr", "value": 78},
    {"name": "May", "value": 90},
    {"name": "Jun", "value": 95},
    {"name": "Jul", "value": 100},
    {"name": "Aug", "value": 110},
    {"name": "Sep", "value": 105},
    {"name": "Oct", "value": 115},
    {"name": "Nov", "value": 120},
    {"name": "Dec", "value": 130}
  ],
  "test_type_distribution": [
    {"name": "Blood Test", "value": 45},
    {"name": "Urinalysis", "value": 28},
    {"name": "Lipid Panel", "value": 22},
    {"name": "Glucose", "value": 18},
    {"name": "Thyroid", "value": 15},
    {"name": "Other", "value": 12}
  ],
  "weekday_distribution": [
    {"name": "Mon", "value": 25},
    {"name": "Tue", "value": 30},
    {"name": "Wed", "value": 35},
    {"name": "Thu", "value": 28},
    {"name": "Fri", "value": 32},
    {"name": "Sat", "value": 15},
    {"name": "Sun", "value": 5}
  ],
  "patient_age_distribution": [
    {"name": "18-24", "value": 15},
    {"name": "25-34", "value": 25},
    {"name": "35-44", "value": 30},
    {"name": "45-54", "value": 22},
    {"name": "55-64", "value": 18},
    {"name": "65+", "value": 20}
  ],
  "gender_distribution": [
    {"name": "Female", "value": 58},
    {"name": "Male", "value": 42}
  ],
  "test_turnaround_time": [
    {"name": "Blood Test", "value": 4},
    {"name": "Urinalysis", "value": 2},
    {"name": "Lipid Panel", "value": 6},
    {"name": "Glucose", "value": 3},
    {"name": "Thyroid", "value": 8}
  ]
})



class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_email = request.data.get('email')
        
        if not new_email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(new_email)
        except ValidationError:
            return Response({'error': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=new_email).exists():
            return Response({'error': 'This email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.email = new_email
        user.is_verfied = False
        user.save()

        return Response({'message': 'Email updated successfully.'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'error': 'Both old and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class SettingsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print('hi')
        try:
            settings = request.user.settings
        except Settings.DoesNotExist:
            Settings(user=request.user).save()
            settings = request.user.settings
            
        serializer = SettingSerializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Settings updated successfully.', ** serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            settings = request.user.settings
        except Settings.DoesNotExist:
            Settings(user=request.user).save()
            settings = request.user.settings
        serializer = SettingSerializer(instance=settings)
        return Response(serializer.data)

class ChangeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully.', **serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)