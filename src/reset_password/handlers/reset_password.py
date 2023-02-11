from reset_password.signals import request_password_reset
from django.dispatch import receiver
from reset_password.views import RequestResetPasswordView


@receiver(request_password_reset, sender=RequestResetPasswordView)
def request_password_reset_handler(
    sender: type[RequestResetPasswordView], token: str, **kwargs
) -> None:
    """handler reset password request"""

    print(token)
