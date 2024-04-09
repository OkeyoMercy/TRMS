from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm

from .models import Company, CustomUser, Driver, Message, Profile

User = get_user_model()
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driving License/National Identification Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']

class TMSAdminstratorCreationForm(UserCreationForm):
    id_number = forms.CharField(max_length=20, required=True)
    driving_license_number = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    region = forms.CharField(max_length=100, required=True)

    class Meta:
        model = get_user_model()  # Use get_user_model for flexibility
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'id_number', 'driving_license_number', 'region']

    def clean_id_number(self):
        user_model = get_user_model()  # Use get_user_model for flexibility
        if user_model.objects.filter(id_number=self.cleaned_data['id_number']).exists():
            raise ValidationError("A user with this ID number already exists.")
        return self.cleaned_data['id_number']

    def clean_driving_license_number(self):
        user_model = get_user_model()  # Use get_user_model for flexibility
        if user_model.objects.filter(driving_license_number=self.cleaned_data['driving_license_number']).exists():
            raise ValidationError("A user with this driving license number already exists.")
        return self.cleaned_data['driving_license_number']

    def clean_email(self):
        user_model = get_user_model()  # Use get_user_model for flexibility
        if user_model.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("A user with this email already exists.")
        return self.cleaned_data['email']

    def save(self, commit=True):
        user = super(TMSAdminstratorCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            tms_admin_group, _ = Group.objects.get_or_create(name='TMS Adminstrator')
            user.groups.add(tms_admin_group)

            # Only create a Profile if not handled by signals
            if not hasattr(user, 'profile'):  # Check if a Profile already exists
                Profile.objects.create(
                    user=user,
                    id_number=self.cleaned_data['id_number'],
                    driving_license_number=self.cleaned_data.get('driving_license_number', '')
                )

        return user

class CompanyManagerForm(forms.ModelForm):
    manager_first_name = forms.CharField(max_length=30)
    manager_last_name = forms.CharField(max_length=30)
    manager_middle_name = forms.CharField(max_length=30, required=False)
    manager_email = forms.EmailField(required=True)
    manager_driving_license_number = forms.CharField(max_length=20)
    manager_id_number = forms.CharField(max_length=20)
    manager_phone_number = forms.CharField(max_length=20)
    role = forms.CharField(widget=forms.TextInput(attrs={'readonly': True}), initial='Manager')

    class Meta:
        model = Company
        fields = ['manager_first_name',
            'manager_middle_name',
            'manager_last_name',
            'manager_email',
            'manager_driving_license_number',
            'manager_id_number',
            'manager_phone_number',
            'role',
            'name',
            'address',
            'region',
            'county',
                  ]
    def clean_manager_id_number(self):
        id_number = self.cleaned_data['manager_id_number']
        if User.objects.filter(id_number=id_number).exists():
            raise ValidationError("A user with this ID number already exists.")
        return id_number

    def clean_manager_driving_license_number(self):
        driving_license_number = self.cleaned_data['manager_driving_license_number']
        if User.objects.filter(driving_license_number=driving_license_number).exists():
            raise ValidationError("A user with this driving license number already exists.")
        return driving_license_number

    def clean_email(self):
        email = self.cleaned_data['manager_email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['manager_phone_number']
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("A user with this email already exists.")
        return phone_number

    def save(self, commit=True):
        with transaction.atomic():
            company = super().save(commit=False)
            user, created = CustomUser.objects.get_or_create(
                email=self.cleaned_data['manager_email'],
                defaults={
                    'first_name': self.cleaned_data['manager_first_name'],
                    'last_name': self.cleaned_data['manager_last_name'],
                    'middle_name': self.cleaned_data.get('manager_middle_name', ''),
                    'id_number': self.cleaned_data['manager_id_number'],
                    'driving_license_number': self.cleaned_data['manager_driving_license_number'],
                    'phone_number': self.cleaned_data['manager_phone_number'],
                    'region': self.cleaned_data['region'],
                    'role': 'Manager'
                }
            )

            if created:
                user.set_password('changeme')
                user.save()
            company.manager = user
            company.save()
            user.company = company
            user.save()
            Profile.objects.get_or_create(user=user, defaults={'profile_image': 'profile_pics/user_profile_pic.png'})
            manager_group, _ = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)

        return company

class DriverRegistrationForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'middle_name', 'last_name', 'id_number', 'driving_license_number', 'email', 'phone_number']

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(DriverRegistrationForm, self).__init__(*args, **kwargs)
        print(self.company)
        if not self.company:
            raise ValueError("Company is required to register a driver.")

    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        if CustomUser.objects.filter(id_number=id_number).exists():
            raise ValidationError("A user with this ID number already exists.")
        return id_number

    def clean_driving_license_number(self):
        driving_license_number = self.cleaned_data['driving_license_number']
        if CustomUser.objects.filter(driving_license_number=driving_license_number).exists():
            raise ValidationError("A user with this driving license number already exists.")
        return driving_license_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Driver'
        user.set_password('changeme')
        if self.company:
            user.company = self.company
            user.region = self.company.region

        if commit:
            user.save()
            driver_group, _ = Group.objects.get_or_create(name='Driver')
            user.groups.add(driver_group)
            profile, created = Profile.objects.get_or_create(user=user)
            if created or not profile.profile_image:
                profile.profile_image = 'profile_pics/user_profile_pic.png'
                profile.save()
            driver, created = Driver.objects.get_or_create(user=user)
            if created or not driver.vehicle_assigned:
                driver.vehicle_assigned = None
                driver.company = self.company
                driver.save()

        return user


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender','recipient']
