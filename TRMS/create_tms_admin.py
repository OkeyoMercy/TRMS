import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRMS.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


def create_tms_admin():
    User = get_user_model()
#CReating a  the first TMS Adminstrator credentials
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

    # Assign the user to the TMS Administrator group
    admin_group, created = Group.objects.get_or_create(name='TMS Administrator')
    tms_admin_user.groups.add(admin_group)

    print("TMS Administrator created and assigned to group.")

if __name__ == "__main__":
    create_tms_admin()
