from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, MessageForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Driver
from .forms import DriverForm
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
    if request.method == 'POST':
        form =DriverForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid ():
            form.save()
            username = request.user.username
            messages.success(request, f'{username}, Your profile is updated.')
            return redirect('/')
    else:
        form = DriverForm(instance= request.user.profile)
    context = {'form':form}  
    return render (request,'TMSapp/driver.html', context)
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

@login_required
def inbox(request):
 try:
        received_messages = Message.objects.filter(recipient=request.user)
        logger.info(f"Messages fetched for {request.user.username}: {received_messages.count()}")
 except Exception as e:
        logger.error(f"Error fetching messages for {request.user.username}: {str(e)}")
        # Consider providing feedback to the user or redirecting to an error page
        raise 
 return render(request, 'inbox.html', {'received_messages': received_messages})
from django.shortcuts import render
from .models import Task, Message

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