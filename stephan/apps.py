from django.apps import AppConfig


class StephanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stephan'

    def ready(self):
        import stephan.signals
