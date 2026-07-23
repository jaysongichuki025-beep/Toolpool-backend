"""
App config for users.
WHY default_auto_field / name: Django needs the full Python path 'apps.users'
so it finds models inside the apps/ package (not a top-level users/ folder).
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'

    def ready(self):
        # Import signals so Profile is auto-created when a User is created
        import apps.users.signals  # noqa: F401
