from rest_framework import serializers
from .models import User, VerificationCode, Profile, Notification, Settings, ForgetPasswordCode, Stage, Question, Session, Messages, Answer, Explanation

from rest_framework import serializers
from .models import AgreementSession
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate


class AgreementSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgreementSession
        fields = [
            "user",                  # add this
            "submitted_at",          # add this
            "motivation_choices",
            "other_motivation",
            "has_confidence_issues",
            "confidence_issues",
            "other_issues",
            "expectations",
            "other_expectations",
        ]
        read_only_fields = ["user", "submitted_at"]  # ✅ ensure user/submitted_at can’t be edited by frontend

    def create(self, validated_data):
        user = self.context["request"].user
        return AgreementSession.objects.create(user=user, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kawrgs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data, is_active = False)
        instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance.set_password(password)
        instance.save()
        return instance
    




    
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class VerificationCodeSerializer(serializers.ModelSerializer): # odn't need it
    class Meta:
        model = VerificationCode
        fields = ['code', 'user']
    
    def validate_code(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('Verfication code length must be 5 numbers exactly')
        return value;

    def validate(self, attrs):
        code = attrs['code']
        user_code = VerificationCode.objects.filter(user=attrs['user'])
        if code != user_code:
            raise serializers.ValidationError('incorrect verification code')
        return super().validate(attrs)
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['major', 'academic_year']
        extra_kwargs = {
            'user': {'read_only': True},
        }
class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['picture']
    
    def upload(self, instance, validated_data):
        instance.picture = validated_data.get('picture', instance.picture)
        instance.save()
        return instance
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ['email_notification', 'appointments_notification', 'results_notification', 'marketing_email']

class ForgetPasswordCodeSerializer(serializers.ModelSerializer): # odn't need it
    class Meta:
        model = VerificationCode
        fields = ['code', 'user']
    
    def validate_code(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('Verfication code length must be 5 numbers exactly')
        return value;

    def validate(self, attrs):
        code = attrs['code']
        user_code = VerificationCode.objects.filter(user=attrs['user'])
        if code != user_code:
            raise serializers.ValidationError('incorrect verification code')
        return super().validate(attrs)





class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class SessionReadSerializer(serializers.ModelSerializer):
    stage = StageSerializer()
    class Meta:
        model = Session
        fields = '__all__'
        
        
class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class ExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Explanation
        fields = '__all__'
from rest_framework import serializers
from .models import User, VerificationCode, Profile, Notification, Settings, ForgetPasswordCode, Stage, Question, Session, Messages, Answer, Explanation

from rest_framework import serializers
from .models import AgreementSession
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate


class AgreementSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgreementSession
        fields = [
            "user",                  # add this
            "submitted_at",          # add this
            "motivation_choices",
            "other_motivation",
            "has_confidence_issues",
            "confidence_issues",
            "other_issues",
            "expectations",
            "other_expectations",
        ]
        read_only_fields = ["user", "submitted_at"]  # ✅ ensure user/submitted_at can’t be edited by frontend

    def create(self, validated_data):
        user = self.context["request"].user
        return AgreementSession.objects.create(user=user, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kawrgs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data, is_active = False)
        instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance.set_password(password)
        instance.save()
        return instance






class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class VerificationCodeSerializer(serializers.ModelSerializer): # odn't need it
    class Meta:
        model = VerificationCode
        fields = ['code', 'user']

    def validate_code(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('Verfication code length must be 5 numbers exactly')
        return value;

    def validate(self, attrs):
        code = attrs['code']
        user_code = VerificationCode.objects.filter(user=attrs['user'])
        if code != user_code:
            raise serializers.ValidationError('incorrect verification code')
        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['major', 'academic_year']
        extra_kwargs = {
            'user': {'read_only': True},
        }
class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['picture']

    def upload(self, instance, validated_data):
        instance.picture = validated_data.get('picture', instance.picture)
        instance.save()
        return instance

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ['email_notification', 'appointments_notification', 'results_notification', 'marketing_email']

class ForgetPasswordCodeSerializer(serializers.ModelSerializer): # odn't need it
    class Meta:
        model = VerificationCode
        fields = ['code', 'user']

    def validate_code(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('Verfication code length must be 5 numbers exactly')
        return value;

    def validate(self, attrs):
        code = attrs['code']
        user_code = VerificationCode.objects.filter(user=attrs['user'])
        if code != user_code:
            raise serializers.ValidationError('incorrect verification code')
        return super().validate(attrs)





class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class SessionReadSerializer(serializers.ModelSerializer):
    stage = StageSerializer()
    class Meta:
        model = Session
        fields = '__all__'


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class ExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Explanation
        fields = '__all__'
from .models import ConfidenceTestResult

class AdminAnswerSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ["user", "stage", "question", "answer", "creation_date"]

    def get_user(self, obj):
        return f"{obj.session.user.first_name} {obj.session.user.last_name}"

    def get_stage(self, obj):
        return obj.session.stage.name

    def get_question(self, obj):
        return obj.question.question


class AdminConfidenceScoreSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ConfidenceTestResult
        fields = ["user", "score", "created_at"]

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
