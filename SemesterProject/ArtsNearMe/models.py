from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Hash the password if it is not already hashed     
        # Call the parent class's save() method to handle the actual saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


