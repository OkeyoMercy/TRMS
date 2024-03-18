from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from TRMS.TRMS.TMSapp.views import calculate_route_score

default_image_path = settings.STATIC_URL + 'assets/img/faces/avatar.jpg'


class Driver(models.Model):
    name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=100)
    licence_number = models.CharField(max_length=100)
    national_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    car_in_charge_of = models.CharField(max_length=100)
    company_from = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null =True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField( blank=True,default='static/assets/img/faces/avatar.jpg')

    def __str__(self):
        return "{self.user.username} 's profile"
    


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} to {self.recipient} at {self.timestamp}'

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title
class YourModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
        

class Route(models.Model):
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance = models.FloatField()  # Distance in kilometers or miles
    def get_best_route(start_location, end_location):
        # Example pseudocode
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