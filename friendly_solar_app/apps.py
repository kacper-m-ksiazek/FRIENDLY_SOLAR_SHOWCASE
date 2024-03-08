from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'friendly_solar_app'

    def ready(self):
        import friendly_solar_app.signals
