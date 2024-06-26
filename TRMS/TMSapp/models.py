from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin, User)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# from TMSapp.views import calculate_route_score
from django.utils.translation import gettext_lazy as _
from TMSapp.utils import calculate_route_score

default_image_path = settings.STATIC_URL + 'assets/img/faces/avatar.jpg'


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
    region = models.CharField(max_length=100)
    role =models.CharField(max_length=30)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Use ID number for authentication
    USERNAME_FIELD = 'id_number'

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_pics/', default='profile_pics/user_profile_pic.png')

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
    
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default='No Subject')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} to {self.recipient.get_full_name()}"
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} to {self.recipient} at {self.timestamp}'

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
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='managing_company')

    def __str__(self):
        return f"Company: {self.name}"
class Vehicle(models.Model):
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"
class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='driver_profile')
    vehicle_assigned = models.OneToOneField('Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='drivers')

    def __str__(self):
        return f"Driver: {self.user.get_full_name()} - {self.user.driving_license_number}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
        

class Route(models.Model):
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance = models.FloatField()
    
    # Distance in kilometers or miles
    def get_best_route(start_location, end_location):
        # Example pseudocode
        from TMSapp.utils import calculate_route_score
        routes = Route.objects.filter(start_location=start_location, end_location=end_location)
        best_route = None
        best_score = 0
        for route in routes:
            # Score routes based on distance, weather, and road conditions
            score = calculate_route_score(route)
            if score > best_score:
                best_score = score
                best_route = route
        return best_route
class Weather(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)  # e.g., "Sunny", "Rainy", etc.
    # More fields as necessary

class RoadCondition(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)


class track(models.Model):
    vehicle_id = models.CharField(max_length=50, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vehicle {self.vehicle_id} at {self.latitude}, {self.longitude} on {self.timestamp}"