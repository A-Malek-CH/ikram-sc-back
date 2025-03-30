from django.contrib import admin
from .models import User, Profile, VerificationCode,Notification


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(VerificationCode)
admin.site.register(Notification)


