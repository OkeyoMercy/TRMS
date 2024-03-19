from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    # List of groups to create
    group_names = ['TMS Administrator', 'Manager', 'Driver']
    
    # Create each group if it doesn't exist
    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f'Group created: {group_name}')

class Migration(migrations.Migration):

    dependencies = [
        # This migration depends on the previous one you mentioned
        ('TMSapp', '0006_rename_content_message_body_and_more'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
