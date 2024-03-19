from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

from .forms import (CompanyManagerForm, DriverForm, LoginForm,
                    TMSAdministratorCreationForm)
from .models import Company, Driver, Message, Task


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['username']  # This can be either a username or an ID number
            password = form.cleaned_data['password']
            
            # Attempt to fetch the user by username or ID number
            try:
                # If the credential is an ID number, try to find a user with that ID number
                user = User.objects.get(Q(username=credential) | Q(profile__id_number=credential))
            except User.DoesNotExist:
                # If no user is found, set user to None
                user = None

            # If a user was found, attempt to authenticate
            if user:
                user = authenticate(username=user.username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                
                # Direct TMS Administrators to the Django admin site
                if user.is_staff or user.groups.filter(name='TMS Administrator').exists():
                    return redirect('/admin/')
                
                # Redirect based on group membership for other users
                elif user.groups.filter(name='Manager').exists():
                    return redirect('manager_dashboard')  # Redirect to Manager dashboard
                elif user.groups.filter(name='Driver').exists():
                    return redirect('driver_dashboard')  # Redirect to Driver dashboard
                else:
                    messages.error(request, 'No role assigned. Please contact the administrator.')
            else:
                messages.error(request, 'Invalid login credentials.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def dashboard_redirect(request):
    # Assuming you have some logic to determine the user's role
    if request.user.groups.filter(name='TMS Administrator').exists():
        return redirect('/admin/')
    elif request.user.groups.filter(name='Driver').exists():
        return redirect('driver_dashboard')
    # Add more conditions as necessary
    else:
        return redirect('generic_dashboard')


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

@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    return render(request, 'driver_detail.html', {'driver': driver})

@login_required
def driver_list_create_update(request, pk=None):
    if pk:
        driver = get_object_or_404(Driver, pk=pk)
        form = DriverForm(request.POST or None, instance=driver)
    else:
        form = DriverForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('driver_list')

    context = {'form': form, 'object': driver if pk else None}
    return render(request, 'driver_form.html', context)

@login_required
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        return redirect('driver_list')
    return render(request, 'driver_confirm_delete.html', {'driver': driver})

def profile(request):
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES, instance=request.user.driver)
        if form.is_valid():
            form.save()
            messages.success(request, f'{request.user.username}, Your profile is updated.')
            return redirect('driver_dashboard')
    else:
        form = DriverForm(instance=request.user.driver)
    return render(request, 'driver_profile.html', {'form': form})

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

@login_required
def tasks_view(request):
    tasks = Task.objects.filter(driver=request.user)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def messages_view(request):
    received_messages = Message.objects.filter(recipient=request.user)
    return render(request, 'messages.html', {'received_messages': received_messages})


#View for the latest models and froms created by mervitz.
class TMSAdministratorCreateView(generic.CreateView):
    form_class = TMSAdministratorCreationForm
    success_url = reverse_lazy('admin_dashboard')
    template_name = 'admin/create_admin.html'

class CompanyCreationView(CreateView):
    model = Company
    form_class = CompanyManagerForm
    template_name = 'admin/register_company.html'  # Adjust the path as necessary
    success_url = reverse_lazy('admin/register_company.html')  # Redirect to the dashboard or any other page after success
    
    def form_valid(self, form):
        # Your logic to handle a valid form
        form.save()
        # Show a success message or something similar
        messages.success(self.request, 'Company and Manager registered successfully.')
        # Render the same registration page with a new empty form
        return render(self.request, self.template_name, {'form': self.form_class()})