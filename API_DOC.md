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
	
	



For later:
http://localhost:8000/supports/create_uploaded_record/:
http://localhost:8000/supports/doctor_suggestion/:







