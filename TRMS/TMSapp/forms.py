from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
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
class TMSAdminstratorCreationForm(ModelForm):
    id_number = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(r'^\d+$', message="ID number must be numeric and contain no spaces or special characters.")
        ]
        )
    driving_license_number = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    region = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number', 'id': 'phonenumber', 'class': 'form-control'})
    )


    class Meta:
        model = User  # Using the custom user model
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'id_number', 'driving_license_number', 'region', 'phone_number']
        
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name.isalpha():
            raise ValidationError("!!First name must contain only letters.")
        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data['middle_name']
        if not middle_name.isalpha():
            raise ValidationError("!!Middle name must contain only letters.")
        return middle_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name.isalpha():
            raise ValidationError("!!Last name must contain only letters.")
        return last_name
    
    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        if User.objects.filter(id_number=id_number).exists():
            raise ValidationError("A user with this ID number already exists.")
        if not id_number.isdigit():
            raise ValidationError("!!ID number must contain only numeric digits.")
        return id_number

    def clean_driving_license_number(self):
        if User.objects.filter(driving_license_number=self.cleaned_data['driving_license_number']).exists():
            raise ValidationError("A user with this driving license number already exists.")
        return self.cleaned_data['driving_license_number']

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("A user with this email already exists.")
        return self.cleaned_data['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True 
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.role = 'TMS Adminstrator'  # Set the default role
        user.set_password('changeme')  # Set default password

        if commit:
            user.save()
            tms_admin_group, _ = Group.objects.get_or_create(name='TMS Adminstrator')
            user.groups.add(tms_admin_group)
            # If the Profile creation is handled by signals, remove the below Profile creation
            if not hasattr(user, 'profile'):  # Check if a Profile already exists
                from .models import Profile  # Ensure you have this impor
                Profile.objects.create(user=user)

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
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'region', 'id_number', 'driving_license_number', 'role']
        read_only_fields = ['first_name', 'middle_name', 'last_name', 'region', 'id_number', 'driving_license_number', 'role']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.read_only_fields:
            self.fields[field].disabled = True   # specify editable fields here
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.isdigit() and not any(char in "+-" for char in phone_number):
            raise forms.ValidationError('Phone number must contain only digits, plus sign (+), or hyphens (-)')

        return phone_number
# class CustomPasswordChangeForm(PasswordChangeForm):
#     class Meta:
#         model = User
#         fields = ('old_password', 'new_password1', 'new_password2')
