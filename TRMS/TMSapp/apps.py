from django.apps import AppConfig


class TMSappConfig(AppConfig):
    name = 'TMSapp'
    
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import TMSapp.models

        from . import signals
        
