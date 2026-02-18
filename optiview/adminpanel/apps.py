from django.apps import AppConfig



class AdminpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminpanel'

    def ready(self):
        from django.conf import settings
        settings.SESSION_COOKIE_NAME = 'adminpanel_session'
