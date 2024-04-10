import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import (CompanyManagerForm, DriverRegistrationForm, LoginForm,
                    MessageForm, ProfileForm, TMSAdminstratorCreationForm)
from .models import (Company, CustomUser, Driver, Message, Profile,
                     RoadCondition, Route, Task, User, Weather)

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
                        return redirect('driver_dashboard')
                    else:
                        messages.error(request, 'No role assigned. Please contact the adminstrator.')
                else:
                    messages.error(request,
                                   'User account is inactive. Please contact the adminstrator.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard_redirect(request):
    if request.user.groups.filter(name='TMS Adminstrator').exists():
        return redirect('/admin/')
    elif request.user.groups.filter(name='Driver').exists():
        return redirect('driver_dashboard')
    elif request.user.groups.filter(name='Manager').exists():
        return redirect('manager_dashboard')
    else:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')

@login_required
def tms_admin_dashboard(request):
    # Ensure the user is a TMS Adminstrator
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, '/admin/')

@login_required
def manager_dashboard(request):
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

@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    return render(request, 'driver_detail.html', {'driver': driver})

@login_required
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        return redirect('driver_list')
    return render(request, 'driver_confirm_delete.html', {'driver': driver})

def compose_message(request):
    if request.method == 'POST':
        body = request.POST.get('content')
        recipient_id = request.POST.get('receiver_id')
        recipient = User.objects.get(id=recipient_id)
        Message.objects.create(sender=request.user, recipient=recipient, body=body)
        return redirect('inbox')
    return render(request, 'compose_message.html')

@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user)
    return render(request, 'inbox.html', {'received_messages': received_messages})
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
            return redirect('inbox')

    return render(request, 'compose_message.html')

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@login_required
def tasks_view(request):
    tasks = Task.objects.filter(driver=request.user)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def messages_view(request):
    received_messages = Message.objects.filter(recipient=request.user)
    return render(request, 'messages.html', {'received_messages': received_messages})


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
    return render(request, 'admin/create_admin.html', {'form': form})


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
    return render(request, 'admin/register_company.html', {'form': form})

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

    return render(request, 'register_driver.html', {'form': form})

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
    
# @login_required
# def password_change_view(request):
#     if request.method == 'POST':
#         form = CustomPasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # Important!
#             messages.success(request, 'Your password was successfully updated!')
#             return redirect('change_password_done')  # Redirect to a success page
#         else:
#             messages.error(request, 'Please correct the error below.')
#     else:
#         form = CustomPasswordChangeForm(user=request.user)
#     return render(request, 'change_password.html', {'form': form})