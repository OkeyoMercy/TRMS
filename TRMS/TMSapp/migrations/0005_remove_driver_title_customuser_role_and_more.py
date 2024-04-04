# Generated by Django 5.0.3 on 2024-04-03 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TMSapp', '0004_alter_profile_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='title',
        ),
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(default='manager', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(default='profile_pics/user_profile_pic.png', upload_to='profile_pics/'),
        ),
        migrations.DeleteModel(
            name='Manager',
        ),
    ]
