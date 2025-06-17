from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paligemma_app'

    def ready(self):
        import paligemma_app.signals
