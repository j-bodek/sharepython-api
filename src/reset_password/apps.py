from django.apps import AppConfig


class ResetPasswordConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reset_password"

    def ready(self) -> None:
        import reset_password.handlers
