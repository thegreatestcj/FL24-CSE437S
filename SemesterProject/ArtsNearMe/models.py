from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import datetime
import pytz

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

class FavoritePlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    place_name = models.CharField(max_length=255)
    place_address = models.CharField(max_length=255)
    place_website = models.URLField(null=True, blank=True)  # Optional website field
    place_id = models.CharField(max_length=100)  # The place ID from Google Maps API

    def __str__(self):
        return f"{self.place_name} - {self.user.username}"

class FavoriteEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    event_name = models.CharField(max_length=255)
    event_start_time = models.CharField(max_length=255)
    place_website = models.URLField(null=True, blank=True)  # Optional website field
    place_id = models.CharField(max_length=100)  # The place ID from Google Maps API

    def __str__(self):
        return f"{self.place_name} - {self.user.username}"
