from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Company, CustomUser, Driver


@receiver(post_migrate)
def setup_default_groups_and_permissions(sender, **kwargs):
    
    ##The TMS Admistrator and their Permissions.
    admin_group, _=Group.objects.get_or_create(name='TMS Adminstrator')
    company_content_type = ContentType.objects.get_for_model(Company)
    customuser_content_type = ContentType.objects.get_for_model(CustomUser)
    admin_permissions = [
        'add_company', 'change_company', 'delete_company', 'view_company',
        'add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',  # Permissions to manage CustomUser instances
    ]
    for permission_codename in admin_permissions:
        content_type = company_content_type if 'company' in permission_codename else customuser_content_type
        permission, _ = Permission.objects.get_or_create(
            codename=permission_codename,
            content_type=content_type,
        )
        admin_group.permissions.add(permission)
        
        #The Mnager and their permissions.
    manager_group, _=Group.objects.get_or_create(name="Manager")
    driver_content_type = ContentType.objects.get_for_model(Driver)
    manager_permissions = [
        'add_driver', 'change_driver', 'view_driver',
    ]
    for permission_codename in manager_permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=permission_codename,
            content_type=driver_content_type,
        )
        manager_group.permissions.add(permission)
        
    