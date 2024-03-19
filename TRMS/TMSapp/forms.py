from fileinput import FileInput
from mailbox import Message

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.models import ModelForm
from django.forms.widgets import FileInput

from .models import (Company, Driver, Manager, Message, Profile,
                     TMSAdministrator, User)


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driving License/National Identification Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Your Password'}))

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['username','national_id']

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'profile_img': FileInput(),
        }
        from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'subject', 'body']


class TMSAdministratorCreationForm(UserCreationForm):
    class Meta:
        model = TMSAdministrator
        fields = ('username', 'first_name', 'middle_name', 'last_name','email', 'id_number', 'driving_license_number', 'title', 'region')

class CompanyManagerForm(forms.ModelForm):
    # Manager's personal details
    manager_first_name = forms.CharField(max_length=30)
    manager_last_name = forms.CharField(max_length=30)
    manager_middle_name = forms.CharField(max_length=30, required=False)
    manager_driving_license_number = forms.CharField(max_length=20)
    manager_id_number = forms.CharField(max_length=20)
    manager_title = forms.CharField(max_length=100, initial='Manager')
    manager_region = forms.CharField(max_length=100)

    class Meta:
        model = Company
        fields = ['name', 'address', 'region', 'county']

    def clean_manager_first_name(self):
        username = self.cleaned_data['manager_first_name']
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def generate_unique_username(self, first_name, last_name):
        base_username = first_name.lower()
        unique_username = base_username
        counter = 1
        while User.objects.filter(username=unique_username).exists():
            unique_username = f"{base_username}{counter}"
            counter += 1
        return unique_username

    def save(self, commit=True):
        company = super().save(commit=False)
        
        # Use the generate_unique_username method to get a unique username
        username = self.generate_unique_username(self.cleaned_data['manager_first_name'], self.cleaned_data['manager_last_name'])
        
        # Set a default password for managers
        default_password = 'manager2'

        # Create a new User instance for the manager with the unique username and default password
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(default_password)  # Set the default password
            user.first_name = self.cleaned_data['manager_first_name']
            user.last_name = self.cleaned_data['manager_last_name']
            user.save()

            # Add the manager to the 'Managers' group
            managers_group, _ = Group.objects.get_or_create(name='Managers')
            user.groups.add(managers_group)

        # Create a new Manager instance linked to the User
        manager, created = Manager.objects.get_or_create(
            user=user,
            defaults={
                'middle_name': self.cleaned_data['manager_middle_name'],
                'driving_license_number': self.cleaned_data['manager_driving_license_number'],
                'id_number': self.cleaned_data['manager_id_number'],
                'title': self.cleaned_data['manager_title'],
                'region': self.cleaned_data['manager_region']
            }
        )

        if commit:
            company.manager = manager
            company.save()
        
        
        
        return company