http://localhost:8000/users/signup/:
	- POST body = {"email", "password", "first_name", "last_name"} -> response = {"email", "message"}
	
http://localhost:8000/users/resend_code/:
	- POST body = {"email"} -> response = {"email", "message"}

http://localhost:8000/users/verify_signup/:
	- POST body = {"email", "code"} -> response = {"email", "message"}

http://localhost:8000/users/login/:
	- POST body = {"email", "password"} -> response = {"token", "role"}


http://localhost:8000/users/my_profile/:
	- GET header = {"Authorization"} -> response = {"id", "email", "first_name", "last_name", "birth_date", "gender", "blood_type", "height"}


http://localhost:8000/users/change_profile_picture/:
	- POST body = {"picture"} + header = {"Authorization"} -> response = {"message"}
	
http://localhost:8000/users/others_profile/<id>/
	- GET header = {"Authorization"} -> response = {"message"}
	
http://localhost:8000/users/others_profile/<id>/:
	- GET header = {"Authorization"} -> response = {"id", "email", "first_name", "last_name", "birth_date", "gender", "blood_type", "height"}
	

http://localhost:8000/users/profile_picture/<id>/:
	- GET header = {"Authorization"} -> response = Image (not json)


http://localhost:8000/users/notifications/:
	- GET header = {"Authorization"} -> response = [{"id", "type", "description", "creation_date", "is_read"}, ...]
	- DELETE body = {"id"}, header = {"Authorization"} -> response = {"message"}

http://localhost:8000/users/notifications_count/:
	- GET header = {"Authorization"} -> response = {"count"}

http://localhost:8000/users/upgrade_premuim/:
	- POST header = {"Authorization"} -> response = {"message"}
	
	

http://localhost:8000/supports/ask_support/: (only patient)
	- POST body = {"title", "content", "is_private", "email"} header = {"Authorization"} -> response = {"id", "title", "content", "is_private", "email", "message"}
	- DELETE body = {"id"}, header = {"Authorization"} -> response = {"message"}

http://localhost:8000/supports/get_support_messages/:
	- GET body = {"private"}, header = {"Authorization"} -> [{"id", "title", "content", "is_private", "email", "message"}, ...]

http://localhost:8000/supports/answer_support_messages/ (only admin)
	- POST body = {"message", "content"} header = {"Authorization"} -> response = {"id", "content", "creation_date", "message", "user"}
	- DELETE body = {"id"}, header = {"Authorization"} -> response = {"message"}

http://localhost:8000/supports/get_answer_support_messages/:
	- GET body = {"id"}, header = {"Authorization"} -> [{"id", "content", "creation_date", "message", "user"}, ...]
	



http://localhost:8000/appointments/patients_appointments/: (for patients)
	- POST body = {"type", "appointment_date"}, header = {"Authorization"} -> {"id", "type", "state", "creation_date", "attendance_date", appointment_date, "is_walk_in", "email", "user", "message"}
	- DELETE body = {"id"}, header = {"Authorization"} -> response = {"message"}
	- GET  header = {"Authorization"} -> [{"id", "type", "state", "creation_date", "attendance_date", appointment_date, "is_walk_in", "email", "user", "message"}, ...]
	

http://localhost:8000/appointments/cancel_appointments/: (for patients)
	- POST body = {"id"}, header = {"Authorization"} -> response = {"message"}

http://localhost:8000/appointments/filterd_appointments/: (for patients to see the appointments to choose an available time)
	- GET para = {"start_date", "end_date", "type"}, header = {"Authorization"} -> [{"state", "creation_date", "appointment_date"}, ...]
	

http://localhost:8000/appointments/walkin_appointments/: (for admin)
	- POST body = {"type", "appointment_date", "email"}, header = {"Authorization"} -> response = {"id", "type", "state", "creation_date", "attendance_date", appointment_date, "is_walk_in", "email", "user", "message"}



http://localhost:8000/appointments/manage_appointment_demands/ for (admin he get the appointment than choose to accept or reject)
	- POST body = {"id"}, header = {"Authorization"} -> { "message"} (for accepting the appointement)
	- DELETE body = {"id"}, header = {"Authorization"} -> response = {"message"} (for rejecting the appointment)
	- GET para = {"start_date", "end_date", "type"}, header = {"Authorization"} -> [{"id", "type", "state", "creation_date", "attendance_date", appointment_date, "is_walk_in", "email", "user", "message"}, ...]

http://localhost:8000/appointments/finish_appointment/: (For admin)
	- POST body = {"id"}, header = {"Authorization"} -> { "message"}
	
http://localhost:8000/appointments/miss_appointments/: (For admin)
	- POST body = {"id"}, header = {"Authorization"} -> { "message"}


some return more (after adding uploader in is_uploaded):

http://localhost:8000/medical_folder/create_record/:
	- POST body = {"type", "image", "appointment", "description"}, header = {"Authorization"} -> {"id", "type", "image", "description", "creation_date", "appointment", "message"}

http://localhost:8000/medical_folder/get_record_image/<id>/:
	- GET header = {"Authorization"} -> Image

http://localhost:8000/medical_folder/get_records/:
	- GET header = {"Authorization"} -> [{"id", "type", "image", "description", "creation_date", "appointment"}, ...]


http://localhost:8000/medical_folder/ai_scan/:
	- POST body = {"model", "medical_record"}, header = {"Authorization"} -> {"id", "model", "result":bool, "description", "creation_date", "medical_record", "message"}
	- GET header = {"Authorization"} -> [{"id", "model", "result":bool, "description", "creation_date", "medical_record", "message"}, ...]
	- DELETE body = {"id"}, header = {"Authorization"} - > {"message"}



http://localhost:8000/medical_folder/manage_doctors/:
	- POST body = {"name", "specialty", "phone", "address":optional, "phone":optional, "email":optional}, header = {"Authorization"} -> {"id", "name", "specialty", "phone", "address", "phone", "email", "creation_date", "message"}
	- GET header = {"Authorization"} -> [{"id", "name", "specialty", "phone", "address", "phone", "email", "creation_date"}, ...]
	- DELETE body = {"id"}, header = {"Authorization"} - > {"message"}
	- PUT body = {"name", "specialty", "phone", "address", "phone", "email"}, header = {"Authorization"} -> {"id", "name", "specialty", "phone", "address", "phone", "email", "creation_date", "message"}
	
	

GET /users/statistics/ not real yet

Response:
{
  "total_patients": 124,
  "total_appointments": 1248,
  "pending_appointments": 5,
  "today_appointments": 8,
  "completion_rate": 98.5,
  "avg_tests_per_day": 24.3,
  "patient_satisfaction": 4.8,
  "monthly_appointments": [
    {"name": "Jan", "value": 65},
    {"name": "Feb", "value": 72},
    {"name": "Mar", "value": 85},
    {"name": "Apr", "value": 78},
    {"name": "May", "value": 90},
    {"name": "Jun", "value": 95},
    {"name": "Jul", "value": 100},
    {"name": "Aug", "value": 110},
    {"name": "Sep", "value": 105},
    {"name": "Oct", "value": 115},
    {"name": "Nov", "value": 120},
    {"name": "Dec", "value": 130}
  ],
  "test_type_distribution": [
    {"name": "Blood Test", "value": 45},
    {"name": "Urinalysis", "value": 28},
    {"name": "Lipid Panel", "value": 22},
    {"name": "Glucose", "value": 18},
    {"name": "Thyroid", "value": 15},
    {"name": "Other", "value": 12}
  ],
  "weekday_distribution": [
    {"name": "Mon", "value": 25},
    {"name": "Tue", "value": 30},
    {"name": "Wed", "value": 35},
    {"name": "Thu", "value": 28},
    {"name": "Fri", "value": 32},
    {"name": "Sat", "value": 15},
    {"name": "Sun", "value": 5}
  ],
  "patient_age_distribution": [
    {"name": "18-24", "value": 15},
    {"name": "25-34", "value": 25},
    {"name": "35-44", "value": 30},
    {"name": "45-54", "value": 22},
    {"name": "55-64", "value": 18},
    {"name": "65+", "value": 20}
  ],
  "gender_distribution": [
    {"name": "Female", "value": 58},
    {"name": "Male", "value": 42}
  ],
  "test_turnaround_time": [
    {"name": "Blood Test", "value": 4},
    {"name": "Urinalysis", "value": 2},
    {"name": "Lipid Panel", "value": 6},
    {"name": "Glucose", "value": 3},
    {"name": "Thyroid", "value": 8}
  ]
}

    path('change_password/',views.ChangePasswordView.as_view()),



http://localhost:8000/users/update_profile/:
  - POST body = {"birth_date", "gender", "blood_type", "height"}, header = {"Authorization"} -> {"id", "birth_date", "gender", "blood_type", "height", "user", "message"}

http://localhost:8000/users/change_email/:
  - POST body = {"email"}, header = {"Authorization"} -> {"message"}

http://localhost:8000/users/change_email/:
  - POST body = {"old_password", "new_password"}, header = {"Authorization"} -> {"message"}

http://localhost:8000/users/settings/:
  - GET header = {"Authorization"} -> {"email_notification", "appointments_notification", "results_notification", "marketing_email"}
  - POST body = {"email_notification", "appointments_notification", "results_notification", "marketing_email"} header = {"Authorization"} -> {"email_notification", "appointments_notification", "results_notification", "marketing_email", "message"}


   
{"email_notification", "appointments_notification", "results_notification", "marketing_email"}
    


For later:
http://localhost:8000/supports/create_uploaded_record/:
	- POST body = {"type", "image", "description"}, header = {"Authorization"} -> {"id", "type", "image", "description", "creation_date", "appointment", "message"}

http://localhost:8000/supports/doctor_suggestion/:







