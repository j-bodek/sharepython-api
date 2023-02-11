from reset_password.signals import request_password_reset
from django.dispatch import receiver
from django.conf import settings
from reset_password.views import RequestResetPasswordView
from reset_password.serializers import RequestResetPasswordSerializer
from emails.tasks import email_sender


@receiver(request_password_reset, sender=RequestResetPasswordView)
def request_password_reset_handler(
    sender: type[RequestResetPasswordView],
    serializer: RequestResetPasswordSerializer,
    **kwargs,
) -> None:
    """handler reset password request by sending reset password email"""

    token = serializer.generate_token()

    # send reset password email
    email_sender.delay(
        email_subject=f"Reset Your Password",
        email_to=serializer.validated_data["email"],
        email_plaintext="emails/reset_password.txt",
        email_template="emails/reset_password.html",
        reset_password_url=settings.RESET_PASSWORD_PAGE_BASE_URL(token=token),
    )
