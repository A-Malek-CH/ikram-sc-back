from django.contrib import admin
from .models import User, Profile, VerificationCode,Notification, Settings, ForgetPasswordCode, Stage, Question, Session, Messages, Answer


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(VerificationCode)
admin.site.register(Notification)
admin.site.register(Settings)
admin.site.register(ForgetPasswordCode)
admin.site.register(Stage)
admin.site.register(Question)
admin.site.register(Session)
admin.site.register(Messages)
admin.site.register(Answer)

