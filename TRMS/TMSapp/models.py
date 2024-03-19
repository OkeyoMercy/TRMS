from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models


class Driver(models.Model):
    name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=100, unique=True)
    licence_number = models.CharField(max_length=100, unique=True)
    national_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    car_in_charge_of = models.CharField(max_length=100)
    company_from = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, related_name='drivers')

    def __str__(self):
        return f"{self.name} - {self.licence_number}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    driving_license_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default='No Subject')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title

class TMSAdministrator(AbstractUser):
    driving_license_number = models.CharField(max_length=20, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100, default='TMS Administrator')
    region = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=30, blank=True, null=True)

    # Specify related_name for groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="tms_admin_groups",
        related_query_name="tmsadmin",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="tms_admin_permissions",
        related_query_name="tmsadmin",
    )

    def __str__(self):
        return self.username

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    first_name = models.CharField(max_length=30, default='DefaultFirstName')
    last_name = models.CharField(max_length=30, default='DefaultLastName')
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    driving_license_number = models.CharField(max_length=20, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100, default='Manager')
    region = models.CharField(max_length=100)

    def __str__(self):
        full_name = f"{self.first_name} {self.middle_name} {self.last_name}" if self.middle_name else f"{self.first_name} {self.last_name}"
        return f"Manager: {full_name}"

class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    region = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    manager = models.OneToOneField(Manager, on_delete=models.CASCADE, related_name='company_managed')

    def __str__(self):
        return f"Company: {self.name}"
