from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model



class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    first_name = None
    last_name = None
    
    USERNAME_FIELD = 'username'
    
   