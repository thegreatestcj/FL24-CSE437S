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
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *

# Initialize environment variables
env = environ.Env()
environ.Env.read_env('.env')
google_maps_api_key = env('GOOGLE_MAPS_API_KEY')
ticketmaster_api_key = env('TICKETMASTER_API_KEY')
artsnearme_map_id = env('ARTSNEARME_MAP_ID')

def index(request):
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

# Nearby Map Display
class MapAPIView(APIView):
    permission_classes = [AllowAny]  # Allow any user, but adjust this based on your needs

    def get(self, request, *args, **kwargs):
        # Handle GET request to render the map page with default values
        context = {
            'google_maps_api_key': google_maps_api_key,
            'artsnearme_map_id': artsnearme_map_id,
            'events': [],  # Default empty events list initially
            'login_status': request.user.is_authenticated,
        }
        return render(request, 'ArtsNearMe/map.html', context)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        # Handle POST request to process user location and return events data
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius = request.data.get('radius', '30')  # Default radius is 30 miles

        if latitude and longitude:
            # Fetch updated events based on user's location
            events = fetch_events_from_ticketmaster(latitude, longitude, radius)
            return Response({'status': 'success', 'events': events}, status=status.HTTP_200_OK)

        return Response({'error': 'Latitude and Longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)


def fetch_events_from_ticketmaster(latitude, longitude, radius):
    # Event tab is more complicated than Place tab.
    # When we click an event marker on the map, it will show all possible events
    # and event dates of that venue. So the place detail page should be venue based.
    # The default event list page should be eventname-venue-based. When events
    # have same venue and name, they share a list item (only time dffers).
    # After MVP Production, we might add event list detail page features when user clicks
    # an item in the default event list.
    ticketmaster_url = f'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'latlong': f'{latitude},{longitude}',
        'radius': radius,
        'unit': 'miles',
        'apikey': ticketmaster_api_key,
    }
    response = requests.get(ticketmaster_url, params=params)
    if response.status_code == status.HTTP_200_OK:
        # events = response.json().get('_embedded', {}).get('events', [])
        # return [{
        #     'name': event['name'],
        #     'start': event['dates']['start']['localDate'],
        #     'description': event['description'],
        #     'latitude': event['_embedded']['venues'][0]['location']['latitude'],
        #     'longitude': event['_embedded']['venues'][0]['location']['longitude'],
        #     'url': event['url'],
        #     'images': event['images'],
        # } for event in events]
        events = response.json().get('_embedded', {}).get('events', [])
        venue_event_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(str)))))
        eventvenue_dates_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(str))))

        for event in events:
            name = event['name']
            images = event['images']
            venue = event['_embedded']['venues'][0]
            placename = venue['name']
            venueId = venue['id'] # unique key for detail pages after clicking on markers
            # venueImages = venue['images'] # may differ from event images
            location = venue['location'] # coordinates for markers
            url = event['url'] # URL is unique once one of venue, eventname, and datetime differs.
            # Format a readable address
            address_lines = venue['address']
            address_lines_str = ', '.join(address_lines.values())
            city = venue['city']['name']
            state = venue['state']['stateCode']
            postalCode = venue['postalCode']
            address = f'{address_lines_str}, {city}, {state} {postalCode}'
            # Format a readable start time
            start = event['dates']['start']
            dateTime = start.get('dateTime')
            dateTime = to_readable_timestr(dateTime) if dateTime else 'N/A'
            # Event list: event-venue-based, identified by unique event-venue tuples
            event_venue = f'{name}, {venueId}'
            eventvenue_dates_dict[event_venue]['eventname'] = name
            eventvenue_dates_dict[event_venue]['start_dates'][dateTime] = url # there might be multiple time slots
            eventvenue_dates_dict[event_venue]['address'] = address
            eventvenue_dates_dict[event_venue]['placename'] = placename
            if eventvenue_dates_dict[event_venue]['images'] is None:
                eventvenue_dates_dict[event_venue]['images'] = images # Set up a potential image gallery for future detail page
            if eventvenue_dates_dict[event_venue]['cover'] is None:
                eventvenue_dates_dict[event_venue]['cover'] = images[0] # Will be used as preview image in the event list
            # Place detail page: venue-based with nested dicts
            # Since it's venue based, there should be only one venueId, whcih would be in the 1st level dict.
            # We suppose the address, placename, and coordinates of a venue never change.
            venue_event_dict[venueId].setdefault('placename', placename)
            venue_event_dict[venueId].setdefault('address', address)
            venue_event_dict[venueId].setdefault('location', location)
            # To avoid overflowing data, we should also limit the image data of venues.
            # venue_event_dict[venueId].setdefault('images', venueImages)
            # venue_event_dict[venueId].setdefault('cover', venueImages[0])
            # A venue might have different events, each with different datetimes and URLs.
            venue_event_dict[venueId][name]['start_dates'][dateTime] = url
    
        return {'eventList': eventvenue_dates_dict, 'mapMarkerDetails': venue_event_dict}
        # return events
    return {}

def to_readable_timestr(datetime_str):
    # Step 1: Parse the ISO 8601 string
    utc_dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    # Mark the datetime object as UTC (since 'Z' indicates UTC)
    utc_dt = utc_dt.replace(tzinfo=pytz.UTC)

    # Step 2: Convert to local time zone (e.g., converting to system's local time zone)
    local_dt = utc_dt.astimezone(timezone.get_current_timezone())

    # Step 3: Format it as a readable string
    readable_string = local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

    return readable_string