# custom_auth.py

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from .models import Driver
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class DriverAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
