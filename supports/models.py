from django.db import models
from users.models import User

class SupportMessage(models.Model):
    title = models.CharField(max_length=512)
    content = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class SupportMessageAnswer(models.Model):
    message = models.ForeignKey(SupportMessage, on_delete=models.CASCADE)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.message.title