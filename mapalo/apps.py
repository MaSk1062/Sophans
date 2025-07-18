from django.apps import AppConfig


class MapaloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mapalo'


    def ready(self):
        import mapalo.signals
