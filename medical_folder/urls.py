from django.urls import path
from . import views

urlpatterns = [
    path('create_record/', views.CreateRecordView.as_view()),
    path('get_record_image/<int:id>/', views.GetRecordImageView.as_view()),
    path('get_records/', views.GetRecordView.as_view()),
    path('ai_scan/', views.AiScanView.as_view()),
    path('manage_doctors/', views.ManageDoctorsView.as_view()),
    path('create_uploaded_record/', views.CreateUploadedRecordView.as_view()),
    path('doctor_suggestion/', views.DoctorSuggestionView.as_view()),
]