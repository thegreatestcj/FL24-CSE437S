from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import datetime
import pytz
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

# No need for custom user model if only using default Django user functionality
# But if you need custom fields:
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, blank=True, null=True)  # New alias field
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class FavoritePlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    place_name = models.CharField(max_length=255)
    place_address = models.CharField(max_length=255)
    place_website = models.URLField(null=True, blank=True)  # Optional website field
    place_id = models.CharField(max_length=100)  # The place ID from Google Maps API
    place_longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Longitude must be between -180 and 180."
    )
    place_latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Latitude must be between -90 and 90."
    )

    class Meta:
        unique_together = ('user', 'place_id')

    def __str__(self):
        return f"{self.place_name} - {self.user.username}"

class FavoriteEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    event_name = models.CharField(max_length=255)
    event_venue = models.CharField(max_length=255)
    event_venue_id = models.CharField(max_length=100)
    event_start_time = models.CharField(max_length=255, null=True, blank=True)
    event_address = models.CharField(max_length=255)
    event_id = models.CharField(max_length=100)
    event_url = models.CharField(max_length=2048, null=True, blank=True)  # Optional website field

    class Meta:
        unique_together = ('user', 'event_id')


    def __str__(self):
        return f"{self.event_name} - {self.user.username}"

class PlaceComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place_id = models.CharField(max_length=100)
    comment = models.TextField()
    # rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'place_id')

    def __str__(self):
        return f"{self.user.username} on {self.place_id}"
