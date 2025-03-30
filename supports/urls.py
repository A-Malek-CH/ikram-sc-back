from django.urls import path
from . import views

urlpatterns = [
    path('ask_support/', views.AskSupporMessagetView.as_view()),
    path('get_support_messages/', views.GetSupportMessageView.as_view()),
    path('answer_support_messages/', views.AnswerSupportMessageView.as_view()),
    path('get_answer_support_messages/', views.GetAnswerSupportMessageView.as_view()),
]