from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import datetime
import pytz
from django.contrib.auth.models import User
from django.db import models

# No need for custom user model if only using default Django user functionality
# But if you need custom fields:
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

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
    event_id = models.CharField(max_length=100)  # The place ID from Google Maps API

    def __str__(self):
        return f"{self.event_name} - {self.user.username}"
