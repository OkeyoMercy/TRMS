# Generated by Django 4.2.3 on 2024-03-15 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TMSapp', '0006_rename_content_message_body_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='YourModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
    ]
