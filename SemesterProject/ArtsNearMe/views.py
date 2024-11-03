from django.urls import reverse_lazy
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_backends
from django.contrib.auth.views import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
import environ
import requests
from datetime import datetime
import pytz
from django.utils import timezone
from collections import defaultdict
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.views.generic import TemplateView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from .serializers import *
from .services import *
from .models import *
from django.http import JsonResponse
import json

# Initialize environment variables
env = environ.Env()
environ.Env.read_env('.env')
google_maps_api_key = env('GOOGLE_MAPS_API_KEY')
ticketmaster_api_key = env('TICKETMASTER_API_KEY')
artsnearme_map_id = env('ARTSNEARME_MAP_ID')

def index(request):
    # print(request.user)
    return render(request, 'ArtsNearMe/home.html', { 'login_status': request.user.is_authenticated, })

class UserRegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'ArtsNearMe/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        backend = get_backends()[0]
        login(self.request, user)  # Automatically log the user in after registration
        return redirect('profile')
    
    def form_invalid(self, form):
    # For an invalid form, simply re-render the page with the form errors
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')  # Redirect to the profile if the user is already logged in
        return super().dispatch(*args, **kwargs)   

class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'ArtsNearMe/login.html'

    def get_success_url(self):
        return reverse_lazy('profile')

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')  # Redirect to the profile if the user is already logged in
        return super().dispatch(*args, **kwargs)

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'ArtsNearMe/profile.html'

    # This attribute defines the login URL to which the user will be redirected
    # if they are not authenticated
    login_url = '/api/login/'  # or use the name of your login URL, e.g., 'login'

    # Optional: You can also set this to redirect to a custom page after login
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any extra context you want to pass to the template
        context['user'] = self.request.user
        context['form'] = ProfileUpdateForm(user=self.request.user, instance=self.request.user.profile)
        return context


class PasswordResetRequestView(PasswordResetView):
    form_class = PasswordResetRequestForm
    template_name = 'ArtsNearMe/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')  # Redirect to profile or home if the user is already logged in
        return super().dispatch(*args, **kwargs)

class PasswordResetRequestDoneView(PasswordResetDoneView):
    template_name = 'ArtsNearMe/password_reset_done.html'
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')  # Redirect to profile or home if the user is already logged in
        return super().dispatch(*args, **kwargs)

class PasswordResetRequestConfirmView(PasswordResetConfirmView):
    form_class = SetNewPasswordForm
    template_name = 'ArtsNearMe/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')  # Redirect to profile or home if the user is already logged in
        return super().dispatch(*args, **kwargs)

class PasswordResetRequestCompleteView(PasswordResetCompleteView):
    template_name = 'ArtsNearMe/password_reset_complete.html'
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')  # Redirect to profile or home if the user is already logged in
        return super().dispatch(*args, **kwargs)

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

# @login_required
def get_map(request):
    # Handle GET request to render the map page with default values
    # print(request.user)
    context = {
        'google_maps_api_key': google_maps_api_key,
        'artsnearme_map_id': artsnearme_map_id,
        'events': [],  # Default empty events list initially
        'login_status': request.user.is_authenticated,
        'is_map': True,
    }
    return render(request, 'ArtsNearMe/map.html', context)

# Nearby Map Display
class MapAPIView(APIView):
    # permission_classes = [AllowAny]  # Allow any user, but adjust this based on your needs
    def post(self, request, *args, **kwargs):
        # Handle POST request to process user location and return events data
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius = request.data.get('radius', '30')  # Default radius is 30 miles
        user_timezone = request.data.get('timezone', 'America/Chicago')

        if latitude and longitude:
            # Fetch updated events based on user's location
            events = fetch_events_from_ticketmaster(latitude, longitude, radius, user_timezone)
            return Response({'status': 'success', 'events': events}, status=status.HTTP_200_OK)

        return Response({'error': 'Latitude and Longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)



def fetch_events_from_ticketmaster(latitude, longitude, radius, user_timezone=None):
    ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'latlong': f'{latitude},{longitude}',
        'radius': radius,
        'unit': 'miles',
        'apikey': ticketmaster_api_key,
    }
    response = requests.get(ticketmaster_url, params=params)

    if response.status_code != status.HTTP_200_OK:
        return {"error": "Failed to fetch data from Ticketmaster"}

    events_data = response.json().get('_embedded', {}).get('events', [])
    
    event_list = []          # List to hold EventVenue instances for the event list view
    map_markers = []         # List to hold MapMarker instances for map markers view

    for event_data in events_data:
        # Extract event and venue data
        name = event_data['name']
        event_id = event_data['id']
        images = event_data['images']
        venue = event_data['_embedded']['venues'][0]
        venue_id = venue['id']
        placename = venue['name']
        location = venue['location']
        url = event_data['url']
        
        # Create a formatted address
        address_lines = venue['address']
        address = ', '.join(address_lines.values()) + f", {venue['city']['name']}, {venue['state']['stateCode']} {venue['postalCode']}"
        
        # Convert event start time to user's timezone
        date_time = event_data['dates']['start'].get('dateTime')
        date_time_str = to_readable_timestr(date_time, user_timezone) if date_time else 'TBD'

        # Create Event instance
        event_instance = Event(
            name=name,
            event_id=event_id,
            date_time=date_time,
            date_time_str=date_time_str,
            venue_id=venue_id,
            url=url
        )

        # Check if EventVenue already exists, if not, create and add to event_list
        event_venue_key = f"{name}, {venue_id}"
        event_venue = next((ev for ev in event_list if ev.event_venue == event_venue_key), None)
        
        if not event_venue:
            event_venue = EventVenue(
                event_venue=event_venue_key,
                eventname=name,
                date_time=date_time,
                date_time_str=date_time_str,
                venue_id=venue_id,
                images=[img['url'] for img in images],
                placename=placename,
                address=address,
                eventdates={date_time_str: [event_id,url]}
            )
            event_list.append(event_venue)
        else:
            # Add date_time_str to existing event_venue's eventdates if it's a new time slot
            event_venue.eventdates[date_time_str] = [event_id, url]

        # Check if MapMarker already exists, if not, create and add to map_markers
        map_marker = next((mm for mm in map_markers if mm.venue_id == venue_id), None)
        
        if not map_marker:
            map_marker = MapMarker(
                venue_id=venue_id,
                placename=placename,
                address=address,
                location=location,
                events=[event_instance],
                images=[img['url'] for img in images]
            )
            map_markers.append(map_marker)
            # print(map_marker.images)
        else:
            # Add event_instance to existing map_marker's events if it's a new event
            map_marker.add_event(event_instance)

    # Serialize event list and map markers
    serialized_event_list = [EventVenueSerializer(event_venue).data for event_venue in event_list]
    serialized_map_markers = [MapMarkerSerializer(marker).data for marker in map_markers]
    # print(images)

    return {'eventList': serialized_event_list, 'mapMarkerDetails': serialized_map_markers}

def to_readable_timestr(datetime_str, user_timezone=None):
    # Step 1: Parse the ISO 8601 string to a datetime object in UTC
    utc_dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
    utc_dt = utc_dt.replace(tzinfo=pytz.UTC)

    # Step 2: Convert to the user's timezone if provided; else use server timezone
    if user_timezone:
        try:
            # Convert to the specified timezone
            user_tz = pytz.timezone(user_timezone)
            local_dt = utc_dt.astimezone(user_tz)
        except pytz.UnknownTimeZoneError:
            # Fallback to server timezone if the user's timezone is invalid
            local_dt = utc_dt.astimezone(timezone.get_current_timezone())
    else:
        # Fallback to server's timezone if no user_timezone is provided
        local_dt = utc_dt.astimezone(timezone.get_current_timezone())

    # Step 3: Format it as a readable string
    readable_string = local_dt.strftime('%Y-%m-%d %H:%M')
    return readable_string

@login_required
@require_POST
def add_favorite_place(request):
    data = json.loads(request.body)
    place, created = FavoritePlace.objects.get_or_create(
        user=request.user,
        place_id=data.get('place_id'),
        defaults={
            'place_name': data.get('place_name'),
            'place_address': data.get('place_address'),
            'place_website': data.get('place_website'),
            'place_longitude': data.get('place_longitude'),
            'place_latitude': data.get('place_latitude'),
        }
    )
    return JsonResponse({'status': 'added' if created else 'already_exists'})

@login_required
@require_POST
def remove_favorite_place(request):
    data = json.loads(request.body)
    try:
        place = FavoritePlace.objects.get(user=request.user, place_id=data.get('place_id'))
        place.delete()
        return JsonResponse({'status': 'removed'})
    except FavoritePlace.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)

# Event favorites
@login_required
@require_POST
def add_favorite_event(request):
    data = json.loads(request.body)
    event, created = FavoriteEvent.objects.get_or_create(
        user=request.user,
        event_id = data.get('event_id'),
        event_name=data.get('event_name'),
        event_venue=data.get('event_venue'),
        event_venue_id=data.get('event_venue_id'),
        event_address=data.get('event_address'),
        event_start_time=data.get('event_start_time'),
        defaults={'event_url': data.get('event_url')},
    )
    return JsonResponse({'status': 'added' if created else 'already_exists'})


@login_required
@require_POST
def remove_favorite_event(request):
    data = json.loads(request.body)
    try:
        event = FavoriteEvent.objects.get(user=request.user, event_id=data.get('event_id'))
        event.delete()
        return JsonResponse({'status': 'removed'})
    except FavoriteEvent.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)


@login_required
def list_favorite_places(request):
    favorites = FavoritePlace.objects.filter(user=request.user).values_list('place_id', flat=True)
    return JsonResponse({'favorites': list(favorites)})


@login_required
def list_favorite_events(request):
    favorites = FavoriteEvent.objects.filter(user=request.user).values_list('event_id', flat=True)
    return JsonResponse({'favorites': list(favorites)})

@login_required
def update_profile(request):
    # if request.method == 'POST':
    #     user = request.user
    #     print(user.profile)

    #     # Ensure the user has a Profile instance
    #     profile, created = Profile.objects.get_or_create(user=user)

    #     # Update Profile fields from POST data
    #     profile.alias = request.POST.get('alias', '').strip()
    #     profile.bio = request.POST.get('bio', '').strip()
    #     profile.location = request.POST.get('location', '').strip()
    #     profile.birth_date = request.POST.get('birth_date') or None

    #     # Handle Profile Image upload
    #     if 'profile_image' in request.FILES:
    #         profile.profile_image = request.FILES['profile_image']

    #     # Save the Profile and User updates
    #     profile.save()
    #     messages.success(request, "Profile updated successfully.")
    #     return redirect('profile')

    # messages.error(request, "There was an error updating your profile.")
    # return redirect('profile')
    user = request.user

    # Handle POST request
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, user=user, instance=user.profile)
        print(user.profile)
        if form.is_valid():
            form.save()  # Save changes to both User and Profile models
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')  # Redirect to the profile page or any desired page
        else:
            messages.error(request, "There was an error updating your profile. Please check the form for details.")
            print(form.errors)
    else:
        # If GET request, initialize form with current user and profile data
        form = ProfileUpdateForm(user=user, instance=user.profile)

    return render(request, 'ArtsNearMe/profile.html', {'form': form})

@login_required
def favorite_places(request):
    favorite_places = FavoritePlace.objects.filter(user=request.user)
    return render(request, 'ArtsNearMe/favorite_places.html', {
        'favorite_places': favorite_places,
    })


@login_required
def favorite_events(request):
    favorite_events = FavoriteEvent.objects.filter(user=request.user, event_start_time__isnull=False)
    tbd_events = FavoriteEvent.objects.filter(user=request.user, event_start_time__isnull=True)
    return render(request, 'ArtsNearMe/favorite_events.html', {
        'favorite_events': favorite_events,
        'tbd_events': tbd_events,
    })