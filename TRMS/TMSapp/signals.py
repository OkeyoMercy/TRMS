from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Company, CustomUser, Driver, Manager, Profile


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create or update a profile whenever a CustomUser is saved.
    """
    # Create a profile for newly created users
    if created:
        Profile.objects.create(user=instance, id_number=instance.id_number, driving_license_number=instance.driving_license_number)
    # Update the profile for existing users
    else:
        profile = Profile.objects.get_or_create(user=instance)[0]
        profile.id_number = instance.id_number
        profile.driving_license_number = instance.driving_license_number
        profile.save()

@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    """
    Signal to assign users to groups based on their specific user type.
    This assumes you have specific user types like 'Manager', 'Driver', etc., identified by their model class.
    """
    if created:
        # Assign to the 'Manager' group if the user instance is a Manager
        if isinstance(instance, Manager):
            manager_group, _ = Group.objects.get_or_create(name='Manager')
            instance.groups.add(manager_group)

        # Assign to the 'Driver' group if the user instance is a Driver
        elif isinstance(instance, Driver):
            driver_group, _ = Group.objects.get_or_create(name='Driver')
            instance.groups.add(driver_group)

        # Assign to the 'TMS Administrator' group if the user is a superuser
        elif instance.is_superuser:
            admin_group, _ = Group.objects.get_or_create(name='TMS Administrator')
            instance.groups.add(admin_group)

@receiver(post_save, sender=Company)
def assign_manager_to_company(sender, instance, created, **kwargs):
    """
    Signal to handle assigning a manager to a company when a company instance is created.
    """
    if created and hasattr(instance, 'manager'):
        # Ensure the manager is assigned to the 'Manager' group
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        instance.manager.groups.add(manager_group)
        instance.manager.save()

# Include any other signals you need for your application
