from django.apps import AppConfig

class DeliveryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'delivery'

    def ready(self):
        from django.conf import settings
        settings.SESSION_COOKIE_NAME = 'delivery_session'
