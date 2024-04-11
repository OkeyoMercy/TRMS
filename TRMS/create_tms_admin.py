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
        password='adminpass',
        first_name='Vitalis',
        middle_name='Ibrahim',
        last_name='Amakalu',
        id_number='40878151',
        driving_license_number='DL123456',
        phone_number='0743720033',
        region='National',
        role='TMS Adminstrator',
        is_staff=True,
        is_superuser=True
    )

    # Assign the user to the TMS Adminstrator group
    admin_group, created = Group.objects.get_or_create(name='TMS Adminstrator')
    tms_admin_user.groups.add(admin_group)

    print("TMS Adminstrator created and assigned to group.")

if __name__ == "__main__":
    create_tms_admin()
