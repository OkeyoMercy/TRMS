from django.apps import AppConfig


class TMSappConfig(AppConfig):
    name = 'TMSapp'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django.db.models.signals import post_migrate

        from . import signals

        # Connect the post_migrate signal to your setup function
        post_migrate.connect(signals.setup_default_groups_and_permissions, sender=self)