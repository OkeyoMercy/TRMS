from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

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
    name = models.CharField(default = 'Okeyo Mercy(Default)',max_length=100, null =True)
    bio = models.TextField(default= 'i am mercy achieng i am a transcountry driver with 4years of experience',blank=True)
    profile_image = models.ImageField(upload_to='C:\\Users\\user\\Desktop\\TRMS\\TRMS\\TRMS\\static\\assets\\img', blank=True,default='static/assets/img/faces/avatar.jpg')

    def __str__(self):
        return "{self.user.username} 's profile"
    
# class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default='No Subject')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    category = models.CharField(max_length=100, default='General')

    def __str__(self):
        return f"From: {self.sender}, To: {self.recipient}, Subject: {self.subject}"

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