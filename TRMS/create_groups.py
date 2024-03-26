import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRMS.settings')
django.setup()

from django.contrib.auth.models import Group


def create_user_groups():
    """
    Creates the following user groups: TMS Administrator, Driver, Manager
    """
    group_names = ["TMS Administrator", "Driver", "Manager"]

    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Group '{group_name}' created.")
        else:
            print(f"Group '{group_name}' already exists.")

if __name__ == "__main__":
    create_user_groups()
    print("User groups created (or already exist).")
