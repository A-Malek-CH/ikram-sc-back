from django.urls import path
from . import views
from .views import ChangeProfileView, LatestConfidenceScoreView
from .views import SubmitConfidenceScoreView

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('resend_code/', views.ResendVerificationCode.as_view()),
    path('verify_signup/', views.SignupVerificationView.as_view()),
    path('my_profile/', views.MyProfileView.as_view()),
    path('change_profile_picture/', views.ChangeProfilePictureView.as_view()),
    path('others_profile/<int:id>/', views.OtherProfileView.as_view()),
path('submit_confidence_score/', SubmitConfidenceScoreView.as_view(), name='submit_confidence_score'),
    path('profile_picture/<int:id>/', views.FetchProfilePictureView.as_view()),
    path('notifications/', views.NotificationsView.as_view()),
    path('notifications_count/', views.NotificationsCountView.as_view()),
    path('upgrade_premuim/', views.UpgradeToPremiumView.as_view()),
    path('statistics/', views.StatisticsView.as_view()),
    path('change_email/', views.ChangeEmailView.as_view()),
    path('change_password/',views.ChangePasswordView.as_view()),
    path('settings/', views.SettingsView.as_view()),
    path('update_profile/', views.ChangeProfileView.as_view()),
    path('reset_password/', views.ForgetPasswordView.as_view()),
    path('verify_reset_password/', views.ForgetPasswordVerificationView.as_view()),
    path('sessions/', views.SessionsView.as_view()),
    path('initialize_chat/', views.InitializeChatView.as_view()),
    path('chat/', views.ChatView.as_view()),
    path('fill_form/', views.FillFormView.as_view()),
    path('reset_session/', views.ResetSessionView.as_view()),
path("change_profile/", ChangeProfileView.as_view(), name="change_profile"),
path('confidence_score/', LatestConfidenceScoreView.as_view()),

]