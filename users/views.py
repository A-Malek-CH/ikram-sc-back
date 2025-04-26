from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from django.http import HttpResponse
from django.conf import settings
from rest_framework import parsers, renderers, status
from users import tools
from users.permissions import IsAdmin, IsNormal
from .serializers import AuthTokenSerializer, SessionReadSerializer, SettingSerializer
from .serializers import UserSerializer, ProfileSerializer, ProfilePictureSerializer, NotificationSerializer, StageSerializer, QuestionSerializer, SessionSerializer, MessagesSerializer, AnswerSerializer
import jwt, datetime
from .models import Explanation, ForgetPasswordCode, Settings, User, VerificationCode, Notification, Stage, Question, Session, Messages, Answer

import random
from django.core.mail import send_mail
from .custom_renderers import ImageRenderer
from rest_framework import generics
from .models import Profile
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
            return Response({'token': token, 'role': user.role, "name": f"{user.first_name} {user.last_name}", "is_premium": user.is_premium})
        user = User.objects.filter(email=request.data['email']).first()
        if user:
            if not user.is_active:
                return Response({'error': 'You need to verify your email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignupView(APIView): 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
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
            stages = Stage.objects.all()
            for i, stage in enumerate(stages):
                session_data = dict()
                session_data['user'] = user.id
                session_data['stage'] = stage.id
                session_data['current_question'] = 0
                session_data['is_unlocked'] = not i
                session_data['is_completed'] = False
                serializer = SessionSerializer(data=session_data)
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
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
        
        progress = Session.objects.filter(user=user, is_completed=True).count()
        progress_ratio = progress / Session.objects.filter(user=user).count()
        total_answers = Answer.objects.filter(session__user=user).count()
        data = dict(**(user_data), **(profile_data), is_premium=user.is_premium, progress=progress, progress_ratio=progress_ratio, total_answers=total_answers)
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
    permission_classes = [IsAuthenticated, IsNormal]
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
            return Response({})



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
            print(e.messages)
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


class ForgetPasswordView(APIView): 
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        if not User.objects.filter(email=email).exists():
            return Response({'error': 'There is no user with such email'}, status=400)
        user = User.objects.get(email=email)
        code = ''.join([str(random.choice(range(10))) for i in range(5)])
        if ForgetPasswordCode.objects.filter(user=user).exists():
            for old_code in ForgetPasswordCode.objects.filter(user=user):
                old_code.delete()
        forget_password_code = ForgetPasswordCode(code=code, user=user)
        forget_password_code.save()
        subject = f'welcome to {settings.APP_NAME}'
        message = f'Hi {user.first_name} {user.last_name} , We received a request to reset your password for <strong>{settings.APP_NAME}, your password reset code is: {code}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (user.email,)
        html_message = f"""
    <html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <p>Hi <strong>{user.first_name} {user.last_name}</strong>,</p>
    <p>We received a request to reset your password for <strong>{settings.APP_NAME}</strong>.</p>
    <p>Your password reset code is:</p>
    <div style="font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px 0;">
      {code}
    </div>
    <p>Please enter this code to reset your password.</p>
    <br>
    <p style="font-size: 12px; color: gray;">If you didn’t request a password reset, you can safely ignore this email.</p>
  </body>
</html>
    """

        send_mail( subject, message, email_from, recipient_list, html_message=html_message, fail_silently=False)
        return Response({'email': user.email, "message": 'A verification code has been sent to your email'}, status=200)

class ForgetPasswordVerificationView(APIView):  
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=400)
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        if not User.objects.filter(email=email).exists():
            return Response({'error': 'There is no user with such email'}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'There is no user with such email'}, status=400)
        user_code = ForgetPasswordCode.objects.filter(user=user.id).first()
        if user_code is None:
            return Response({'error': 'There is no verification code for this user'}, status=400)
        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required'}, status=400)
        try:
            validate_password(password, user=user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=400)
        if code == user_code.code:
            user.set_password(password)
            user.save()
            user_code.delete()
            return Response({'email': user.email, 'message': 'Your password has been changed'}, status=200)
        return Response({'error': 'Can\'t verify code'}, status=400)
    
    def put(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=400)
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        if not User.objects.filter(email=email).exists():
            return Response({'error': 'There is no user with such email'}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'There is no user with such email'}, status=400)
        user_code = ForgetPasswordCode.objects.filter(user=user.id).first()
        if user_code is None:
            return Response({'error': 'There is no verification code for this user'}, status=400)
        
        if code == user_code.code:
            return Response({'email': user.email, 'message': 'The code you entered is valid'}, status=200)
        return Response({'error': 'Can\'t verify code'}, status=400)


class SessionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        sessions = Session.objects.filter(user=user).order_by('stage__order')
        serializer = SessionReadSerializer(instance=sessions, many=True)
        return Response(data=serializer.data, status=200)

class ResetSessionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        session.current_question = 0
        session.is_completed = False
        session.save()
        messages = Messages.objects.filter(session=session)
        for message in messages:
            message.delete()
        answers = Answer.objects.filter(session=session)
        for answer in answers:
            answer.delete()
        return Response({'message': 'Session reset successfully'}, status=200)

class InitializeChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        if not session.is_unlocked:
            return Response({'error': 'This stage is locked'}, status=403)
        if session.is_completed:
            return Response({'error': 'This stage is already completed'}, status=403)
        stage = session.stage
        if session.in_explanation:
            session.in_explanation = False
            session.save()
            explanations = Explanation.objects.filter(stage=stage)
            if explanations.exists():
                messages = []
                for explanation in explanations:
                    message = tools.process_explanation(explanation.explanation)
                    instance = Messages.objects.create(session=session, message=message, is_user=False)
                    messages.append(instance)
                serializer = MessagesSerializer(instance=messages, many=True)
                return Response(serializer.data, status=200)
            
        question = Question.objects.filter(stage=stage).order_by('order')[session.current_question]
        serializer = QuestionSerializer(instance=question)
        message = tools.process_init_question(question.question)
        Messages.objects.create(session=session, message=message, is_user=False)
        return Response(data={'messages': [serializer.data]}, status=200)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        if not session.is_unlocked:
            return Response({'error': 'This stage is locked'}, status=403)
        if session.is_completed:
            return Response({'error': 'This stage is already completed'}, status=403)
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message is required'}, status=400)
        messages = Messages(session=session, message=message, is_user=True)
        messages.save()
        question = Question.objects.filter(stage=session.stage).order_by('order')[session.current_question]
        is_answer, ai_answer = tools.process_answer(message, question.question)
        if is_answer:
            answer = Answer(session=session, question=question, answer=message)
            answer.save()
            session.current_question += 1
            if session.current_question >= Question.objects.filter(stage=session.stage).count():
                session.is_completed = True
                session.save()
        ai_messages = Messages(session=session, message=ai_answer, is_user=False)
        ai_messages.save()
        serializer = MessagesSerializer(instance=ai_messages)
        return Response(data=[serializer.data], status=200)
    
    def get(self, request):
        user = request.user
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        if not session.is_unlocked:
            return Response({'error': 'This stage is locked'}, status=403)
        messages = Messages.objects.filter(session=session).order_by('creation_date')
        serializer = MessagesSerializer(instance=messages, many=True)
        return Response(data=serializer.data, status=200)

class FillFormView(APIView):
    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        if not session.is_unlocked:
            return Response({'error': 'This stage is locked'}, status=403)
        if session.stage.is_chat:
            return Response({'error': 'This stage is a chat stage'}, status=403)
        if session.is_completed:
            return Response({'error': 'This stage is already completed'}, status=403)
        question = Question.objects.filter(stage=session.stage).order_by('order')[session.current_question]
        answer = Answer(session=session, question=question, answer=request.data.get('answer'))
        answer.save()
        serializer = AnswerSerializer(instance=answer)
        return Response(data=serializer.data, status=200)
        
    
    def get(self, request):
        user = request.user
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        if not session.is_unlocked:
            return Response({'error': 'This stage is locked'}, status=403)
        if session.stage.is_chat:
            return Response({'error': 'This stage is a chat stage'}, status=403)
        questions = Question.objects.filter(stage=session.stage).order_by('order')
        serializer = QuestionSerializer(instance=questions, many=True)
        return Response(data=serializer.data, status=200)