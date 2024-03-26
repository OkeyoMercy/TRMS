from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, password=None, **extra_fields):
        if not id_number:
            raise ValueError(_('The ID number field must be set'))
        user = self.model(id_number=id_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(id_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    id_number = models.CharField(max_length=100, unique=True)
    driving_license_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Use ID number for authentication
    USERNAME_FIELD = 'id_number'

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(CustomUser):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

class TMSAdministrator(CustomUser):
    title = models.CharField(max_length=50, default='TMS Administrator')
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"TMS Adminstrator: {self.get_full_name()}"

class Manager(CustomUser):
    title = models.CharField(max_length=50, default='Manager')

    def __str__(self):
        return f"Manager: {self.get_full_name()}"
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default='No Subject')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} to {self.recipient.get_full_name()}"

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title


class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    region = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    manager = models.OneToOneField(Manager, on_delete=models.CASCADE, related_name='company_managed')

    def __str__(self):
        return f"Company: {self.name}"
class Vehicle(models.Model):
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"
class Driver(CustomUser):
    title = models.CharField(max_length=50, default='Driver')
    vehicle_assigned = models.OneToOneField(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_driver')
    # Add other fields specific to drivers here

    def __str__(self):
        return f"Driver: {self.get_full_name()} - {self.driving_license_number}"
