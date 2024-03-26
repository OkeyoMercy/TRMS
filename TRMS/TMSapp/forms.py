from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Company, Driver, Manager, Profile, TMSAdministrator


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

    class Meta:
        model = TMSAdministrator
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'id_number', 'driving_license_number', 'title', 'region']

    def clean_id_number(self):
        if Profile.objects.filter(id_number=self.cleaned_data['id_number']).exists():
            raise ValidationError("A user with this ID number already exists.")
        return self.cleaned_data['id_number']

    def clean_driving_license_number(self):
        if Profile.objects.filter(driving_license_number=self.cleaned_data['driving_license_number']).exists():
            raise ValidationError("A user with this driving license number already exists.")
        return self.cleaned_data['driving_license_number']

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("A user with this email already exists.")
        return self.cleaned_data['email']

    def save(self, commit=True):
        user = super(TMSAdministratorCreationForm, self).save(commit=False).save(commit=False)
        user.username = self.cleaned_data.get('driving_license_number') or self.cleaned_data['id_number']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Assign user to "TMS Administrator" group
            tms_admin_group, _ = Group.objects.get_or_create(name='TMS Administrator')
            user.groups.add(tms_admin_group)

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
    manager_title = forms.CharField(max_length=100, initial='Manager')
    manager_region = forms.CharField(max_length=100)

    class Meta:
        model = Company
        fields = ['name', 'address', 'region', 'county']

    def clean_manager_id_number(self):
        id_number = self.cleaned_data['manager_id_number']
        if Manager.objects.filter(id_number=id_number).exists() or Profile.objects.filter(id_number=id_number).exists():
            raise ValidationError("A user with this ID number already exists.")
        return id_number

    def clean_manager_driving_license_number(self):
        driving_license_number = self.cleaned_data['manager_driving_license_number']
        if Profile.objects.filter(driving_license_number=driving_license_number).exists():
            raise ValidationError("A user with this driving license number already exists.")
        return driving_license_number

    def clean_email(self):
        email = self.cleaned_data['manager_email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        company = super().save(commit=False)

        username = self.cleaned_data.get('manager_driving_license_number') or self.cleaned_data['manager_id_number']
        user = User.objects.create_user(username=username, email=self.cleaned_data['manager_email'])
        user.set_password('manager')
        user.save()

        if commit:
            company.save()
            
            manager_group, _ = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)

            Profile.objects.create(
                user=user,
                id_number=self.cleaned_data['manager_id_number'],
                driving_license_number=self.cleaned_data.get('manager_driving_license_number', '')
            )

        return company
class DriverRegistrationForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)

    class Meta:
        model = Driver
        fields = ['id_number', 'phone_number', 'driving_license_number',]
        widgets = {
            'profile_image': forms.FileInput(),
        }
