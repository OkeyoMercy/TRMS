from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import requests
from .forms import LoginForm, MessageForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Driver, Profile, Weather
from .forms import DriverForm
from .forms import ProfileForm
from django.contrib.auth.models import User
from .models import Message
from .models import Task, Message
from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Message
import logging
from django.http import HttpResponse
from .models import Route
from .models import Route, Weather, RoadCondition
from django.shortcuts import render
from .models import Task, Message
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                return redirect('driver')  # Redirect all users to the drivers page after login
            else:
                messages.error(request, 'Invalid login credentials.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# Dashboard views for each user type
@login_required
def tms_admin_dashboard(request):
    # Ensure the user is a TMS Administrator
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, '/admin/')

@login_required
def manager_dashboard(request):
    # Ensure the user is a Manager
    if not request.user.groups.filter(name='Manager').exists():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, 'manager_dashboard.html')

@login_required
def driver_dashboard(request):
    # Ensure the user is a Driver
    if not request.user.groups.filter(name='Driver').exists():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, 'driver_dashboard.html')
def driver (request):
    objects = Driver.objects.all()
    return render (request,'driver.html', {'drivers':driver})
def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, 'driver_list.html', {'drivers': drivers})

@login_required
def driver_detail(request, pk):
    driver = Driver.objects.get(pk=pk)
    return render(request, 'driver_detail.html', {'driver': driver})

@login_required
def driver_create(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('driver_list')
    else:
        form = DriverForm()
    return render(request, 'driver_form.html', {'form': form})

@login_required
def driver_update(request, pk):
    driver = Driver.objects.get(pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('driver_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'driver_form.html', {'form': form})

@login_required
def driver_delete(request, pk):
    driver = Driver.objects.get(pk=pk)
    if request.method == 'POST':
        driver.delete()
        return redirect('driver_list')
    return render(request, 'driver_confirm_delete.html', {'driver': driver})
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form =ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid ():
            form.save()
            username = request.user.username
            messages.success(request, f'{username}, Your profile is updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance= request.user.profile)
    context = {'form':form}  
    return render (request,'driver.html', context)
def compose_message(request):
    admin_users = User.objects.filter(is_staff=True, is_superuser=True) # Get all users except the current user

    if request.method == 'POST':
        body = request.POST.get('body')
        recipient_id = request.POST.get('recipient_id')

        try:
            recipient = User.objects.get(id=recipient_id)
            Message.objects.create(sender=request.user, recipient=recipient, body=body)
            messages.success(request, 'Message sent successfully.')
            return redirect('inbox')
        except User.DoesNotExist:
            messages.error(request, 'Recipient not found.')
            return redirect('inbox')  # Adjust the redirect as necessary

    return render(request, 'compose_message.html') 

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def tasks_view(request):
    tasks = Task.objects.filter(driver=request.user)
    return render(request, 'tasks.html', {'tasks': tasks})

def messages_view(request):
    received_messages = Message.objects.filter(recipient=request.user)
    return render(request, 'messages.html', {'received_messages': received_messages})
def send_message_to_admin(request):
    logger.debug("Attempting to send a message to admin.")
    admin_users = User.objects.filter(is_superuser=True)
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
    return render(request, 'send_message_to_admin.html', {'form': form})

def admin_inbox(request):
    if request.user.is_superuser:
        inbox_messages = Message.objects.filter(recipient=request.user)
        return render(request, 'admin_inbox.html', {'inbox_messages': inbox_messages})
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
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'inbox.html', {'received_messages': received_messages, 'sent_messages': sent_messages, 'users': users})

@login_required
def send_message(request, recipient_id):
    if request.method == 'POST':
        recipient = User.objects.get(id=recipient_id)
        content = request.POST.get('content', '')
        message = Message.objects.create(sender=request.user, recipient=recipient, content=content)
        return render(request, 'send_messages.html', {'message_sent': True, 'recipient_id': recipient_id})
    # Added the following for debugging
    print("Recipient ID:", recipient_id)
    return render(request, 'send_messages.html', {'recipient_id': recipient_id})




def update_weather_for_route(route):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={route.end_location}&appid={settings.OPENWEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    # Parse the data and update the Weather model
    weather_condition = data['weather'][0]['main']  # Simplified example
    Weather.objects.update_or_create(route=route, defaults={'condition': weather_condition})

def calculate_route_score(route, weather, road_condition):
    """
    Calculates a score for a given route based on distance, weather, and road condition.

    :param route: Route object containing information about the route.
    :param weather: Weather object containing weather conditions for the route.
    :param road_condition: RoadCondition object containing road conditions for the route.
    :return: A numerical score representing the desirability of the route.
    """
    # Base score is the distance - shorter routes are preferred
    score = route.distance

    # Adjust score based on weather conditions
    if weather.condition == 'Good':
        score -= 10  # Subtract points for good weather
    elif weather.condition == 'Bad':
        score += 15  # Add points for bad weather

    # Adjust score based on road conditions
    if road_condition.condition == 'Good':
        score -= 10  # Subtract points for good road conditions
    elif road_condition.condition == 'Bad':
        score += 20  # Add points for bad road conditions

    return score

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

        return render(request, 'best_route.html', {'route': best_route})