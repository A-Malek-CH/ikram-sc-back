from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('appointments/', include('appointments.urls')),
    path('supports/', include('supports.urls')),
    path('medical_folder/', include('medical_folder.urls')),
]
