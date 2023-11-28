from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    name = "habhub.users"
    verbose_name = "Users"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
