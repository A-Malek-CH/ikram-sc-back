from django.contrib import admin
from .models import SupportMessage, SupportMessageAnswer

admin.site.register(SupportMessage)
admin.site.register(SupportMessageAnswer)
