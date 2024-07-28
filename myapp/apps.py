from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

# Payment Integration
    def ready(self):
        import myapp.signals

    def ready(self):
        import myapp.hooks