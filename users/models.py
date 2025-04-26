from django.db import models
from django.contrib.auth.models import AbstractUser
from . import managers
import os

class User(AbstractUser):
    ROLE_CHOICES = [('normal', 'Normal'), ('admin', 'Admin')]

    def get_upload_to(self, filename):
        return os.path.join('images', 'profile_pictures', str(self.pk), filename)
    
    DEFAULT_PICTURE = 'images/profile_pictures/default_profile_picture.jpg'

    email = models.EmailField(unique=True, max_length=254, verbose_name='email address')
    password = models.CharField(max_length=128, verbose_name='password')
    first_name = models.CharField(max_length=128, verbose_name='first name')
    last_name = models.CharField(max_length=128, verbose_name='last name')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='normal')
    is_premium = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    picture = models.ImageField(upload_to=get_upload_to, default=DEFAULT_PICTURE)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = managers.UserManager()

class Profile(models.Model):
    GENDER_CHOICES = [('F', 'Female'), ('M', 'Male')]
    BLOOD_TYPE_CHOICES = [('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O+', 'O+'),
                           ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('O-', 'O-')]
    
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.email


class VerificationCode(models.Model):
    code = models.CharField(max_length=6)
    creationDate = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.email

class Notification(models.Model):
    NOTIFICATION_TYPES = [('message', 'Message'), ('alert', 'Alert')]
    type = models.CharField(max_length=32, choices=NOTIFICATION_TYPES)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.type

class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_notification = models.BooleanField(default=False)
    appointments_notification = models.BooleanField(default=True)
    results_notification = models.BooleanField(default=True)
    marketing_email = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"Settings for {self.user.email}"


class ForgetPasswordCode(models.Model):
    code = models.CharField(max_length=6)
    creationDate = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.email








class Stage(models.Model):
    order = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_chat = models.BooleanField(default=True)
    

class Question(models.Model):
    order = models.IntegerField()
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)

    class Meta:
        unique_together = ('order', 'stage')

class Explanation(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    explanation = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Explanation for {self.stage.name}"


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    current_question = models.IntegerField(default=0)
    in_explanation = models.BooleanField(default=True)
    is_unlocked = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'stage')

    def __str__(self):
        return f"Session for {self.user.email} at stage {self.stage.name}"

class Messages(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    message = models.TextField()
    is_user = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.session.user.email} at stage {self.session.stage.name}"

class Answer(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for {self.session.user.email} at stage {self.session.stage.name}"