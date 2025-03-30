from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('resend_code/', views.ResendVerificationCode.as_view()),
    path('verify_signup/', views.SignupVerificationView.as_view()),
    path('my_profile/', views.MyProfileView.as_view()),
    path('change_profile_picture/', views.ChangeProfilePictureView.as_view()),
    path('others_profile/<int:id>/', views.OtherProfileView.as_view()),
    path('profile_picture/<int:id>/', views.FetchProfilePictureView.as_view()),
    path('reset_password/', views.ResetPassword.as_view()),
    path('create_verification_record/', views.CreateVerificationRecordView.as_view()),
    path('notifications/', views.NotificationsView.as_view()),
]
