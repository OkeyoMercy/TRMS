import logging

import requests
import urllib3
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import router, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from .forms import (CompanyManagerForm, DriverRegistrationForm, LoginForm,
                    MessageForm, ProfileForm, TMSAdminstratorCreationForm)
from .models import (Company, CustomUser, Driver, Message, Profile,
                     RoadCondition, Route, Task, Weather)
#testing route
from .utils import (calculate_route_score, fetch_road_condition_for_route,
                    fetch_weather_for_route, get_route_now)

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=credential, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    if user.groups.filter(name='TMS Adminstrator').exists():
                        return redirect('/admin/')
                    elif user.groups.filter(name='Manager').exists():
                        return redirect('manager_dashboard')
                    elif user.groups.filter(name='Driver').exists():
                        return redirect('route_view')
                    else:
                        messages.error(request, 'No role assigned. Please contact the adminstrator.')
                else:
                    messages.error(request,
                                   'User account is inactive. Please contact the adminstrator.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form,'show_profile_component': False})

@login_required
def dashboard_redirect(request):
    request.session['show_profile_component'] = True
    if request.user.groups.filter(name='TMS Adminstrator').exists():
        return redirect('tms_admin_dashboard')
    elif request.user.groups.filter(name='Driver').exists():
        return redirect('driver_dashboard')
    elif request.user.groups.filter(name='Manager').exists():
        return redirect('manager_dashboard')
    else:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')

@login_required
def tms_admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    show_profile_component = request.session.get('show_profile_component', False)
    return render(request, 'admin/base.html', {'show_profile_component': show_profile_component})

@login_required
def manager_dashboard(request):
    if not request.user.groups.filter(name='Manager').exists():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    show_profile_component = request.session.get('show_profile_component', False)
    return render(request, 'manager_dashboard.html', {'show_profile_component': show_profile_component})

@login_required
def driver_dashboard(request):
    if not request.user.groups.filter(name='Driver').exists():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    show_profile_component = request.session.get('show_profile_component', False)
    return render(request, 'driver_dashboard.html', {'show_profile_component': show_profile_component})  # Adjust the template path as needed

@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    show_profile_component = request.session.get('show_profile_component', False)
    return render(request, 'driver_detail.html', {'driver': driver, 'show_profile_component': show_profile_component})

@login_required
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        return redirect('driver_list')
    return render(request, 'driver_confirm_delete.html', {'driver': driver, 'show_profile_component': False})

def compose_message(request):
    if request.method == 'POST':
        body = request.POST.get('content')
        recipient_id = request.POST.get('receiver_id')
        recipient = CustomUser.objects.get(id=recipient_id)
        Message.objects.create(sender=request.user, recipient=recipient, body=body)
        return redirect('inbox')
    return render(request, 'compose_message.html', {'show_profile_component': False})

@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user)
    users= CustomUser.objects.exclude(id=request.user.id)
    print(users)
    return render(request, 'inbox.html', {'received_messages': received_messages, 'users':users, 'show_profile_component': False})

def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    # print(profile)
    if request.method == 'POST':
        form =ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid ():
            form.save()
            username = request.user.first_name
            messages.success(request, f'{username}, Your profile is updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance= request.user.profile)
    context = {'form':form}
    print("The url is"+request.user.profile.profile_image.url)
    return render (request,'driver_dashboard.html', {'form':form, 'show_profile_component': False})

def compose_message(request):
    admin_users = CustomUser.objects.filter(is_staff=True, is_superuser=True) # Get all users except the current user
    if request.method == 'POST':
        body = request.POST.get('body')
        recipient_id = request.POST.get('recipient_id')

        try:
            recipient = CustomUser.objects.get(id=recipient_id)
            Message.objects.create(sender=request.user, recipient=recipient, body=body)
            messages.success(request, 'Message sent successfully.')
            return redirect('inbox')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Recipient not found.')
            return redirect('inbox')

    return render(request, 'compose_message.html', {'show_profile_component': False})

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@login_required
def tasks_view(request):
    tasks = Task.objects.filter(driver=request.user)
    return render(request, 'tasks.html', {'tasks': tasks, 'show_profile_component': False})

@login_required
def messages_view(request):
    received_messages = Message.objects.filter(recipient=request.user)
    return render(request, 'messages.html', {'received_messages': received_messages, 'show_profile_component': False})

@login_required
def tms_adminstrator_create_view(request):
    if request.method == 'POST':
        form = TMSAdminstratorCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adminstrator registered successfully.')
            return redirect('add_tms_admin')
    else:
        form = TMSAdminstratorCreationForm()
    return render(request, 'admin/create_admin.html', {'form': form,'show_profile_component': False})

@login_required
@transaction.atomic
def company_creation_view(request):
    if not request.user.groups.filter(name='TMS Adminstrator').exists():
        return HttpResponseForbidden("You don't have permission to access this page.")
    if request.method == 'POST':
        form = CompanyManagerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company and Manager registered successfully.')
            return redirect('add_company')
    else:
        form = CompanyManagerForm()
    return render(request, 'admin/register_company.html', {'form': form, 'show_profile_component': False})

@login_required
def driver_registration_view(request):
    print(f"User Role: {request.user.role}")
    print(f"User Company: {request.user.company}")
    if not (request.user.role == 'Manager' and hasattr(request.user, 'company')):
        messages.error(request, "You are not authorized to perform this action.")
        return HttpResponseForbidden("You are not authorized to perform this action.")
    company = request.user.company
    print(company)
    if not company:
        messages.error(request, "No associated company found for this manager.")
        return HttpResponseForbidden("You don't have permission to access this page.")
    form = DriverRegistrationForm(request.POST or None, request.FILES or None, company=company)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Driver registered successfully.')
        return redirect('add_driver')  # Redirect to the list of drivers
    return render(request, 'register_driver.html', {'form': form, 'show_profile_component': False})

def send_message_to_admin(request):
    logger.debug("Attempting to send a message to admin.")
    admin_users = CustomUser.objects.filter(is_superuser=True)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Fetch the admin user. Adjust this according to how you identify admins.
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                message = form.save(commit=False)
                message.sender = request.user  # Set the sender to the current user
                message.recipient = admin_user  # Set the recipient to the admin user
                message.save()
                return redirect('message_sent_success')  # Redirect to a success page
            else:
                logger.warning("Attempted to send message to admin, but no admin user found.")
                pass
    else:
        form = MessageForm()
    return render(request, 'send_message_to_admin.html', {'form': form, 'show_profile_component': False})

def admin_inbox(request):
    if request.user.is_superuser:
        inbox_messages = Message.objects.filter(recipient=request.user)
        return render(request, 'admin_inbox.html', {'inbox_messages': inbox_messages, 'show_profile_component': False})
    else:
        # Redirect the user to the home page or another appropriate page
        return HttpResponseForbidden("You are not authorized to view this page.")
def send_notification(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'New Message',
            f'You have a new message from {instance.sender.username}.',
            'from@example.com',
            [instance.recipient.email],
            fail_silently=False,
        )
        
@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'inbox.html', {'received_messages': received_messages, 'sent_messages': sent_messages, 'users': users, 'show_profile_component': False})

@login_required
def send_message(request, recipient_id):
    if request.method == 'POST':
        recipient = CustomUser.objects.get(id=recipient_id)
        content = request.POST.get('content', '')
        message = Message.objects.create(sender=request.user, recipient=recipient, content=content)
        return render(request, 'send_messages.html', {'message_sent': True, 'recipient_id': recipient_id, 'show_profile_component': False})
    # Added the following for debugging
    print("Recipient ID:", recipient_id)
    return render(request, 'send_messages.html', {'recipient_id': recipient_id, 'show_profile_component': False})

def update_weather_for_route(route):
    
    if router.end_location and hasattr(settings, 'OPENWEATHER_API_KEY'):
         url = f"http://api.openweathermap.org/data/2.5/weather?q={route.end_location}&appid={settings.OPENWEATHER_API_KEY}"
    else:
         FileNotFoundError
    
    response = requests.get(urllib3)
    data = response.json()
    # Parse the data and update the Weather model
    weather_condition = data['weather'][0]['main']  # Simplified example
    Weather.objects.update_or_create(route=route, defaults={'condition': weather_condition})

def calculate_best_route(request):
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    
    # Fetch routes using a third-party API
    routes = fetch_routes(origin, destination, settings.MAPBOX_API_KEY)

    best_route = None
    best_score = None

    for route in routes['routes']:
        route_id = route['id']
        
        # Fetch weather and road conditions for this route (you'll need to implement these functions)
        weather = fetch_weather_for_route(route_id)
        road_condition = fetch_road_condition_for_route(route_id)
        
        # Calculate a score for the route (you'll need to implement this logic based on your criteria)
        score = calculate_route_score(route, weather, road_condition)

        if best_score is None or score < best_score:
            best_score = score
            best_route = route
    
    if best_route:
        # Render a template with the best route information
        return render(request, 'best_route.html', {'route': best_route,'show_profile_component': False})
    else:
        return HttpResponse("No suitable route found.")


def display_best_route(request):
    if request.method == 'GET':
        start_location = request.GET.get('start')
        end_location = request.GET.get('end')

        # Fetch routes that match the start and end locations
        potential_routes = Route.objects.filter(start_location=start_location, end_location=end_location)

        if not potential_routes.exists():
            return HttpResponse("No routes found for the specified locations.", status=404)

        best_route = None
        best_route_score = float('inf')

        for route in potential_routes:
            try:
                weather = Weather.objects.get(route=route)
                road_condition = RoadCondition.objects.get(route=route)
            except (Weather.DoesNotExist, RoadCondition.DoesNotExist):
                continue  # Skip this route if weather or road condition data is missing

            score = route.distance  # Base score on distance
            if weather.condition == 'Good':
                score -= 10  # Better score for good weather
            if road_condition.condition == 'Good':
                score -= 10  # Better score for good road condition

            if score < best_route_score:
                best_route_score = score
                best_route = route

        if not best_route:
            return HttpResponse("Unable to determine the best route with the available data.", status=404)

        return render(request, 'best_route.html', {'route': best_route, 'show_profile_component': False})

def track (request):
    tracking  = {
        'vehicle_id': '123ABC',
        'latitude': '40.7128',
        'longitude': '-74.0060',
        'timestamp': '2024-03-22 12:00:00'
    }
    return render (request,'tracking.html', {'tracking':tracking, 'show_profile_component': False})

def fetch_routes(origin, destination, api_key):
    # Example using Mapbox Directions API
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin};{destination}"
    params = {
        "access_token": api_key,
        "geometries": "geojson"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Process and return relevant data from the response
        return data
    else:
        # Log error or take appropriate action
        print(f"Error fetching route data: {response.status_code}")
        return None
def find_best_route(request):
    # Get origin and destination from request
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')

    # Fetch potential routes for the given origin and destination
    potential_routes = Route.objects.filter(start_location=origin, end_location=destination)

    if not potential_routes.exists():
        return HttpResponse("No routes found for the given locations.")

    best_route = None
    best_score = float('inf')  # Initialize with infinity; lower scores are better

    # Evaluate each potential route
    for route in potential_routes:
        # Fetch weather and road condition for the route
        weather = fetch_weather_for_route(route.id)
        road_condition = fetch_road_condition_for_route(route.id)

        # Calculate a score for the route based on various factors
        score = calculate_route_score(route, weather, road_condition)

        # Determine if this is the best route so far
        if score < best_score:
            best_score = score
            best_route = route

    # Render a response based on the best route found
    if best_route:
        context = {'route': best_route, 'score': best_score}
        return render(request, 'best_route.html', context,{'show_profile_component': False} )
    else:
        return HttpResponse("Unable to determine the best route.")

def route_view(request):
    user = request.user
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')[:4]
    # Only proceed if both start and end locations are provided
    if 'start' in request.GET and 'end' in request.GET:
        start = request.GET['start']
        end = request.GET['end']

    return render(request, 'driver_dashboard.html', {'user':user,'received_messages':received_messages, 'show_profile_component': False})

def get_route(request):
    api_key = settings.GEOAPIFY_API_KEY  # Assuming you've added this in your settings.py
    start = request.GET.get('start', 'default_start')  # Replace 'default_start' with a default or error handling
    end = request.GET.get('end', 'default_end')  # Replace 'default_end' with a default or error handling
    
    base_url = f'https://api.geoapify.com/v1/routing?waypoints={start}|{end}&mode=drive&apiKey={api_key}'

    response = requests.get(base_url)  # Use 'base_url' instead of 'url'
    if response.status_code == 200:
        route_data = response.json()
        
        # Additional error handling for API-specific errors
        if route_data.get('error'):
            return JsonResponse({'error': 'Failed to fetch route data due to API error'}, status=500)
        
        return render(request, 'driver_dashboard.html', {'route_data': route_data})
    else:
        return JsonResponse({'error': 'Failed to fetch route data'}, status=response.status_code)
    
    
    
    
#testing route
def render_route(request):
    return render(request, 'mbasemap.html', {'show_profile_component': False})


def profile_page(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            username = request.user.first_name
            messages.success(request, f'{username}, your profile has been updated.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {'form': form, 'show_profile_component': False})

def dprofile_page(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            username = request.user.first_name
            messages.success(request, f'{username}, your profile has been updated.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'dprofile.html', {'form': form, 'show_profile_component': False})

def dashboard_view(request):
    context = {
        'show_profile_component': 'true',
    }
    return render(request, 'dashboard.html', context, {'show_profile_component': False})

def fetch_route(from_lat, from_lon, to_lat, to_lon, api_key):
    waypoints = f"{from_lat},{from_lon}|{to_lat},{to_lon}"
    url = f"https://api.geoapify.com/v1/routing?waypoints={waypoints}&mode=drive&details=instruction_details&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # returns the route in JSON format
    else:
        return