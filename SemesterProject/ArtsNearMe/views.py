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


# Initialize environment variables
env = environ.Env()
environ.Env.read_env('.env')
google_maps_api_key = env('GOOGLE_MAPS_API_KEY')
ticketmaster_api_key = env('TICKETMASTER_API_KEY')

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
def map_view(request):
    latitude = request.GET.get('latitude') or '37.7749'
    longitude = request.GET.get('longitude') or '-122.4194'
    radius = request.GET.get('radius', '30')  # Default radius is 30 miles
    
    if not latitude or not longitude:
        return JsonResponse({'error': 'Latitude and Longitude are required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    events = fetch_events_from_ticketmaster(latitude, longitude, radius) 

    context = {        
        'google_maps_api_key': google_maps_api_key,
        'events': events,
        'login_status': request.user.is_authenticated,
        
    }
    return render(request, 'ArtsNearMe/map.html', context)


def fetch_events_from_ticketmaster(latitude, longitude, radius):
    ticketmaster_url = f'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'latlong': f'{latitude},{longitude}',
        'radius': radius,
        'unit': 'miles',
        'apikey': ticketmaster_api_key,
    }
    response = requests.get(ticketmaster_url, params=params)
    if response.status_code == status.HTTP_200_OK:
        events = response.json().get('_embedded', {}).get('events', [])
        return [{
            'name': event['name'],
            'start': event['dates']['start']['localDate'],
            'description': event['info'] if 'info' in event else 'No description available.',
            'latitude': event['_embedded']['venues'][0]['location']['latitude'],
            'longitude': event['_embedded']['venues'][0]['location']['longitude']
        } for event in events]
    return []

