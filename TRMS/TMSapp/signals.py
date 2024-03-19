from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def add_to_admin_group(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'is_tms_admin') and instance.is_tms_admin:
        admin_group, _ = Group.objects.get_or_create(name='Administrator')
        instance.groups.add(admin_group)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()