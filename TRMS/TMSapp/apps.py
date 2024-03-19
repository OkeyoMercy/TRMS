from django.apps import AppConfig


class TMSappConfig(AppConfig):
    name = 'TMSapp'

    def ready(self):
        from . import signals

