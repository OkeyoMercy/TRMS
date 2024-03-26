from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Manager, Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            id_number=getattr(instance, 'id_number', None),
            driving_license_number=getattr(instance, 'driving_license_number', None)
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=User)
def add_to_admin_group(sender, instance, created, **kwargs):
    if created and instance.groups.filter(name='TMS Administrator').exists():
        admin_group, _ = Group.objects.get_or_create(name='Administrator')
        instance.groups.add(admin_group)

@receiver(post_save, sender=User)
def create_or_update_manager(sender, instance, created, **kwargs):
    if hasattr(instance, 'profile') and instance.groups.filter(name='Manager').exists():
        manager, _ = Manager.objects.update_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'id_number': instance.profile.id_number,
                'driving_license_number': instance.profile.driving_license_number,
                'region': instance.profile.region
            }
        )
