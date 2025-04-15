from django.db import models
from users.models import User


class Appointment(models.Model):
    APPOINTMENT_TYPES = [("bone","X-Ray"),
  ("pneumonia", "Pneumonia"),
  ("blood-test","Blood Test"),
  ("urinalysis","Urinalysis"),
  ("glucose","Blood Glucose"),
  ("cholesterol", "Cholesterol Panel"),
  ("thyroid","Thyroid Panel"),
  ("complete-blood-count","Complete Blood Count"),
  ("liver-function","Liver Function Test"),
  ("kidney-function","Kidney Function Test")]
    APPOINTMENT_STATES = [('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected'),('F', 'Finished'), ('M', 'Missed'),('C', 'Canceled'), ('D', 'Done')]

    type = models.CharField(max_length=64, choices=APPOINTMENT_TYPES)
    state = models.CharField(max_length=1, choices=APPOINTMENT_STATES, default='P')
    creation_date = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateTimeField()
    attendance_date = models.DateTimeField(null=True, blank=True)
    is_walk_in = models.BooleanField(default=False)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f'Appointment id {self.id} by {self.user.email if self.user else self.email}'