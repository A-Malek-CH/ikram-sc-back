http://localhost:8000/users/signup/:
	- POST body = {"email", "password", "first_name", "last_name"} -> response = {"email", "message"}
	
http://localhost:8000/users/resend_code/:
	- POST body = {"email"} -> response = {"email", "message"}

http://localhost:8000/users/verify_signup/:
	- POST body = {"email", "code"} -> response = {"email", "message"}

http://localhost:8000/users/login/:
	- POST body = {"email", "password"} -> response = {"token", "role"}


http://localhost:8000/users/my_profile/:
	- GET header = {"Authorization"} -> response = {"id", "email", "first_name", "last_name", "birth_date", "gender", "speciality"}


http://localhost:8000/users/change_profile_picture/:
	- POST body = {"picture"} + header = {"Authorization"} -> response = {"message"}
	
http://localhost:8000/users/others_profile/<id>/
	- GET header = {"Authorization"} -> response = {"message"}
	
http://localhost:8000/users/others_profile/<id>/:
	- GET header = {"Authorization"} -> response = {"id", "email", "first_name", "last_name", "birth_date", "gender",  "speciality"}
	

http://localhost:8000/users/profile_picture/<id>/:
	- GET header = {"Authorization"} -> response = Image (not json)


http://localhost:8000/users/notifications/:
	- GET header = {"Authorization"} -> response = [{"id", "type", "description", "creation_date", "is_read"}, ...]
	- DELETE body = {"id"}, header = {"Authorization"} -> response = {"message"}

http://localhost:8000/users/notifications_count/:
	- GET header = {"Authorization"} -> response = {"count"}

http://localhost:8000/users/upgrade_premuim/:
	- POST header = {"Authorization"} -> response = {"message"}


http://localhost:8000/users/update_profile/:
  - POST body = {"birth_date", "gender",  "speciality"}, header = {"Authorization"} -> {"id", "birth_date", "gender",  "speciality", "user", "message"}

http://localhost:8000/users/change_email/:
  - POST body = {"email"}, header = {"Authorization"} -> {"message"}

http://localhost:8000/users/change_password/:
  - POST body = {"old_password", "new_password"}, header = {"Authorization"} -> {"message"}

http://localhost:8000/users/settings/:
  - GET header = {"Authorization"} -> {"email_notification", "appointments_notification", "results_notification", "marketing_email"}
  - POST body = {"email_notification", "appointments_notification", "results_notification", "marketing_email"} header = {"Authorization"} -> {"email_notification", "appointments_notification", "results_notification", "marketing_email", "message"}


http://localhost:8000/users/reset_password/:
  - POST body = {"email"} -> {"email", "password"}

    
http://localhost:8000/users/verify_reset_password/:
  - PUT body = {"email", "code"} -> {"message", "email"}
  - POST body = {"email", "code", "password"} -> {"message", "email"}


http://localhost:8000/users/sessions/
  - GET header = {"Authorization"} -> [{"id", "stage": {"id", "order", "name", "description", "is_chat"}, "current_question", "is_unlocked", "is_completed", "creation_date", "user"}]

http://localhost:8000/users/initialize_chat/:
  - POST body = {"session_id"}, header = {"Authorization"} -> [{"id", "message", "is_user", "creation_date", "session"}, ...]


http://localhost:8000/users/chat/:
  - POST body = {"session_id", "message"}, header = {"Authorization"} -> [{"id", "message", "is_user", "creation_date", "session"}, ...]
  - GET params = {"session_id"}, header = {"Authorization"} -> [{"id", "message", "is_user", "creation_date", "session"}, ...]



