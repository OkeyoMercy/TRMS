from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Attempt to retrieve an existing user by driving license number
try:
    tms_admin_user = User.objects.get(driving_license_number='DL123456')
    print("User with this driving license number already exists.")
except User.DoesNotExist:
    # If no user exists with this driving license number, create a new one
    tms_admin_user = User.objects.create_user(
        email='admin@example.com',
        password='admin_password',
        first_name='Admin',
        last_name='User',
        id_number='123456789',
        driving_license_number='DL123456',
        phone_number='1234567890',
        is_staff=True,
        is_superuser=True
    )
    # Add user to the TMS Administrator group
    tms_admin_group, _ = Group.objects.get_or_create(name='TMS Administrator')
    tms_admin_user.groups.add(tms_admin_group)
    print("TMS administrator created and added to the group.")
