from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Create your models here.

class OtpModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
