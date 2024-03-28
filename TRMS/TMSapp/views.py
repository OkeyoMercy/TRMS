from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

from .forms import (CompanyManagerForm, DriverRegistrationForm, LoginForm,
                    TMSAdministratorCreationForm)
from .models import Company, Driver, Manager, Message, Task


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

                    if user.groups.filter(name='TMS Administrator').exists():
                        return redirect('/admin/')
                    elif user.groups.filter(name='Manager').exists():
                        return redirect('manager_dashboard')
                    elif user.groups.filter(name='Driver').exists():
                        return redirect('driver_dashboard')
                    else:
                        messages.error(request, 'No role assigned. Please contact the administrator.')
                else:
                    messages.error(request,
                                   'User account is inactive. Please contact the administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard_redirect(request):
    if request.user.groups.filter(name='TMS Administrator').exists():
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
        form = DriverRegistrationForm(request.POST or None, instance=driver)
    else:
        form = DriverRegistrationForm(request.POST or None)

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

def Profile(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, request.FILES, instance=request.user.driver)
        if form.is_valid():
            form.save()
            messages.success(request, f'{request.user.username}, Your profile is updated.')
            return redirect('driver_dashboard')
    else:
        form = DriverRegistrationForm(instance=request.user.driver)
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


class TMSAdministratorCreateView(CreateView):
    form_class = TMSAdministratorCreationForm
    template_name = 'admin/create_admin.html'
    success_url = reverse_lazy('admin/create_admin.html')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Administrator registered successfully.')
        return super(TMSAdministratorCreateView, self).form_valid(form)


class CompanyCreationView(CreateView):
    model = Company
    form_class = CompanyManagerForm
    template_name = 'admin/register_company.html'
    success_url = reverse_lazy('admin/register_company.html')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Company and Manager registered successfully.')
        return super(CompanyCreationView, self).form_valid(form)
    
class DriverRegistrationView(LoginRequiredMixin, CreateView):
    model = Driver
    form_class = DriverRegistrationForm
    template_name = 'manager/register_driver.html'
    success_url = reverse_lazy('manager/register_driver.html')

    def form_valid(self, form):
        driver = form.save(commit=False)
        manager_profile = Manager.objects.get(user=self.request.user)
        driver.company = manager_profile.company_managed
        driver.save()
        return super().form_valid(form)
