from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer
import resend
from django.conf import settings

from django.http import HttpResponse
# Add StreamingHttpResponse to your imports
from django.http import StreamingHttpResponse
# Add the json library for formatting the stream
from rest_framework import viewsets, permissions
from .models import Note, UserAchievement, Achievement
from .serializers import NoteSerializer, UserAchievementSerializer, AchievementSerializer
from rest_framework import viewsets, permissions
from .models import Note
from .serializers import NoteSerializer

import json
import time # We'll use this for a tiny delay
from django.conf import settings
from rest_framework import parsers, renderers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ConfidenceTestResult
from .models import ConfidenceTestResult
from users import tools
from users.permissions import IsAdmin, IsNormal
from .serializers import AuthTokenSerializer, SessionReadSerializer, SettingSerializer, AdminAnswerSerializer, \
    AdminConfidenceScoreSerializer
from .serializers import UserSerializer, ProfileSerializer, ProfilePictureSerializer, NotificationSerializer, StageSerializer, QuestionSerializer, SessionSerializer, MessagesSerializer, AnswerSerializer
import jwt, datetime
from .models import Explanation, ForgetPasswordCode, Settings, User, VerificationCode, Notification, Stage, Question, Session, Messages, Answer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import AgreementSession
from .serializers import AgreementSessionSerializer

import random
from django.core.mail import send_mail
from .custom_renderers import ImageRenderer
from rest_framework import generics
from .models import Profile
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

def send_resend_email(to_email, subject, html_message):
    """Send transactional email via Resend API"""
    try:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": "Thiqati <noreply@ikram.xyz>" ,  # You can change this later to your domain
            "to": [to_email],
            "subject": subject,
            "html": html_message,
        })
        print(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Email sending failed for {to_email}: {e}")


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
            return Response({'token': token, 'role': "admin" if user.is_superuser else user.role, "name": f"{user.first_name} {user.last_name}", "is_premium": user.is_premium})
        user = User.objects.filter(email=request.data['email']).first()
        if user:
            if not user.is_active:
                return Response({'error': 'You need to verify your email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgreementSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # ✅ Return just a flag to simplify frontend logic
        if AgreementSession.objects.filter(user=request.user).exists():
            return Response({"submitted": True})
        else:
            return Response({"submitted": False})

    def post(self, request):
        # Prevent duplicate submission
        if AgreementSession.objects.filter(user=request.user).exists():
            return Response({"detail": "Already submitted"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AgreementSessionSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"submitted": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllAnswersView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        answers = Answer.objects.select_related("session", "question", "session__user").all()
        data = [
            {
                "user": f"{answer.session.user.first_name} {answer.session.user.last_name}",
                "stage": answer.session.stage.name,
                "question": answer.question.question,
                "answer": answer.answer,
                "timestamp": answer.creation_date,
            }
            for answer in answers
        ]
        return Response(data, status=200)


class AllConfidenceScoresView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        scores = ConfidenceTestResult.objects.select_related("user").all()
        data = [
            {
                "user": f"{score.user.first_name} {score.user.last_name}",
                "score": score.score,
                "timestamp": score.created_at,
            }
            for score in scores
        ]
        return Response(data, status=200)
class AdminExportView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        answers = Answer.objects.select_related("session", "question", "session__user").all()
        scores = ConfidenceTestResult.objects.select_related("user").all()

        answer_data = AdminAnswerSerializer(answers, many=True).data
        score_data = AdminConfidenceScoreSerializer(scores, many=True).data

        return Response({
            "session_answers": answer_data,
            "confidence_scores": score_data,
        })


class SubmitConfidenceScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        score = request.data.get("score")
        try:
            score = float(score)
        except (ValueError, TypeError):
            return Response({"error": "Invalid score"}, status=status.HTTP_400_BAD_REQUEST)

        result = ConfidenceTestResult.objects.create(user=request.user, score=score)
        return Response({"message": "Score saved", "id": result.id}, status=status.HTTP_201_CREATED)
class LatestConfidenceScoreView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        score = ConfidenceTestResult.objects.filter(user=request.user).order_by('-created_at').first()

        return Response({"score": score.score if score else None})


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            # Create profile immediately with major and academic_year if provided
            major = request.data.get("major", "")
            academic_year = request.data.get("academic_year", "")
            Profile.objects.create(user=instance, major=major, academic_year=academic_year)
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

        send_resend_email(data['email'], subject, html_message)
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

        send_resend_email(user.email, subject, html_message)
        return Response({'email': user.email, "message": 'A verification code has been sent to your email'}, status=200)

class SignupVerificationView(APIView):  
    def post(self, request):
        code = request.data['code'] 
        user = User.objects.filter(email=request.data['email']).first()
        user_code = VerificationCode.objects.filter(user=user.id).first()   
        if code == user_code.code:
            user_code.delete()
            user.is_active = True

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
        profile = user.profile

        picture_file = request.FILES.get('picture')

        if not picture_file:
            return Response({'error': 'No picture file provided'}, status=400)

        profile.picture = picture_file
        profile.save()

        return Response({'message': 'Profile picture updated successfully'}, status=200)

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

        send_resend_email(user.email, subject, html_message)
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
        session_id = request.data.get("session_id")

        if not session_id:
            return Response({"error": "Session ID is required"}, status=400)

        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({"error": "Session not found"}, status=404)

        # Reset session metadata
        session.current_question = 0
        session.is_completed = False
        session.in_explanation = True  # ✅ mark as needing explanations
        session.save()

        # Delete all messages
        Messages.objects.filter(session=session).delete()

        # Delete all answers
        Answer.objects.filter(session=session).delete()

        return Response({"message": "Session has been reset."}, status=200)
def stream_chat_initialization(session):
    """
    A generator function that yields explanations and the first question
    as Server-Sent Events (SSE).
    """
    try:
        stage = session.stage

        # 1. Process and stream explanations if they haven't been sent yet
        if session.in_explanation:
            explanations = Explanation.objects.filter(stage=stage).order_by('id')
            for explanation in explanations:
                # Process with Gemini API
                message_text = tools.process_explanation(explanation.explanation)
                # Save the message to the database
                msg_obj = Messages.objects.create(session=session, message=message_text, is_user=False)
                # Serialize the new message object
                serializer = MessagesSerializer(instance=msg_obj)
                # Yield the data in SSE format
                yield f"data: {json.dumps(serializer.data)}\n\n"
                time.sleep(0.1) # Small delay to ensure messages are sent separately

            # Mark explanations as done
            session.in_explanation = False
            session.save()

        # 2. Process and stream the first question if it's the start of the session
        if session.current_question == 0 and not Messages.objects.filter(session=session, is_user=False, message__icontains="?").exists():
            question = Question.objects.filter(stage=stage).order_by('order').first()
            if question:
                ai_message_text = tools.process_init_question(question.question)
                msg_obj = Messages.objects.create(session=session, message=ai_message_text, is_user=False)
                serializer = MessagesSerializer(instance=msg_obj)
                yield f"data: {json.dumps(serializer.data)}\n\n"
                time.sleep(0.1)

    except Exception as e:
        # In case of an error during the stream, send an error message
        error_data = {"error": f"An error occurred during streaming: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"


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

        # If the session is already completed, no need to stream anything.
        if session.is_completed:
            return Response([], status=200)

        # This is the key change: return a StreamingHttpResponse
        # It calls our new generator function to get the data piece by piece.
        response = StreamingHttpResponse(stream_chat_initialization(session), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'  # Ensure no caching of the stream
        return response


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')
        message = request.data.get('message')

        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        if not message:
            return Response({'error': 'Message is required'}, status=400)

        session = Session.objects.filter(user=user, id=session_id).first()
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        if not session.is_unlocked:
            return Response({'error': 'This stage is locked'}, status=403)

        # Save user message
        Messages.objects.create(session=session, message=message, is_user=True)

        # Check if session is already completed (after user last message)
        questions = Question.objects.filter(stage=session.stage).order_by('order')
        if session.current_question >= len(questions):
            # Send final congratulatory message only once
            if not Messages.objects.filter(session=session, message__icontains="أحسنت").exists():
                final_msg = "🎉 أحسنت! لقد أكملت هذه المرحلة بنجاح. أنت تبلي بلاءً حسنًا! استمر في التقدم!"
                final_ai = Messages.objects.create(session=session, message=final_msg, is_user=False)
                return Response(data=[MessagesSerializer(instance=final_ai).data], status=200)
            return Response(data=[], status=200)

        # Normal case: answer + move to next
        current_question = questions[session.current_question]
        Answer.objects.create(session=session, question=current_question, answer=message)

        session.current_question += 1
        if session.current_question >= len(questions):
            session.is_completed = True
            # 🔓 Unlock next session
            next_session = Session.objects.filter(user=user, stage__order=session.stage.order + 1).first()
            if next_session:
                next_session.is_unlocked = True
                next_session.save()

        session.save()

        ai_messages = []

        # Optional feedback
        _, feedback = tools.process_answer(message, current_question.question)
        ai_feedback = Messages.objects.create(session=session, message=feedback, is_user=False)
        ai_messages.append(ai_feedback)

        # Next question if any
        if not session.is_completed:
            next_question = questions[session.current_question]
            prompt = tools.process_init_question(next_question.question)
            ai_question = Messages.objects.create(session=session, message=prompt, is_user=False)
            ai_messages.append(ai_question)
        else:
            final_msg = "🎉 أحسنت! لقد أكملت هذه المرحلة بنجاح. استمر في رحلتك نحو التحسن."
            final_ai = Messages.objects.create(session=session, message=final_msg, is_user=False)
            ai_messages.append(final_ai)

        serializer = MessagesSerializer(instance=ai_messages, many=True)
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


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class AllAchievementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Achievement.objects.all().order_by("id")
        data = AchievementSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=200)

class MyAchievementsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = (
            UserAchievement.objects
            .filter(user=request.user)
            .select_related("achievement")
            .order_by("-unlocked_at")
        )
        data = UserAchievementSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=200)
