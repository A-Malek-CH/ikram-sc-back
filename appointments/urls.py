from django.urls import path
from . import views

urlpatterns = [
    path('patients_appointments/', views.PatientAppointmentView.as_view()),
    path('cancel_appointments/', views.CancelAppointmentView.as_view()),
    path('filterd_appointments/', views.FilteredAppointmentsView.as_view()),
    path('walkin_appointments/', views.WalkInAppointmentView.as_view()),
    path('manage_appointment_demands/', views.ManageAppointmentDemandsView.as_view()),
    path('finish_appointment/', views.FinishAppointmentView.as_view()),
    path('miss_appointments/', views.MarkMissedAppointmentView.as_view()),
]
