from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Company, Driver, Manager, Message, Profile

User = get_user_model()
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driving License/National Identification Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']

class TMSAdministratorCreationForm(UserCreationForm):
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
        user = super(TMSAdministratorCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            tms_admin_group, _ = Group.objects.get_or_create(name='TMS Administrator')
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
    manager_title = forms.CharField(widget=forms.TextInput(attrs={'readonly': True}), initial='Manager')
    manager_region = forms.CharField(max_length=100)

    class Meta:
        model = Company
        fields = ['manager_first_name','manager_middle_name', 'manager_last_name', 'manager_email',
                  'manager_driving_license_number', 'manager_id_number', 'manager_title'
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

def save(self, commit=True):
    company = super().save(commit=False)  # Save company data without creating the object yet

    # Create user using CustomUserManager (assuming it's named 'CustomUserManager')
    username = self.cleaned_data.get('manager_driving_license_number') or self.cleaned_data['manager_id_number']
    user = User.objects.create_user(
        id_number=self.cleaned_data['manager_id_number'],
        email=self.cleaned_data['manager_email'],
        password='manager',  # Replace with a secure password generation method
        first_name=self.cleaned_data['manager_first_name'],
        last_name=self.cleaned_data['manager_last_name'],
        middle_name=self.cleaned_data.get('manager_middle_name', ''),
    )
    user.set_password('manager')  # Needs a secure password generation method (placeholder here)
    user.save()  # Save the user object

    if commit:
        company.save()  # Save the company object after user creation
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        user.groups.add(manager_group)

        # Create Profile with data from cleaned form data
        Profile.objects.create(
            user=user,
            id_number=self.cleaned_data['manager_id_number'],
            driving_license_number=self.cleaned_data.get('manager_driving_license_number', '')
        )

    return company
class DriverRegistrationForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['id_number', 'phone_number', 'driving_license_number']
        widgets = {
            'profile_image': forms.FileInput(),
        }
        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender','recipient']

