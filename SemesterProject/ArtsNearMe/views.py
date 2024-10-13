from django.views import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
import environ
import requests
from django.http import JsonResponse
from datetime import datetime
import pytz
from django.utils import timezone
from collections import defaultdict
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny

# Initialize environment variables
env = environ.Env()
environ.Env.read_env('.env')
google_maps_api_key = env('GOOGLE_MAPS_API_KEY')
ticketmaster_api_key = env('TICKETMASTER_API_KEY')
artsnearme_map_id = env('ARTSNEARME_MAP_ID')

def index(request):
    return render(request, 'ArtsNearMe/index.html')

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'ArtsNearMe/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():  # Validate the form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')  # Change 'home' to your home view name
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()  # Create an empty form instance

    return render(request, 'ArtsNearMe/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

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