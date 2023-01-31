from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from emails.tasks import email_sender


@receiver(post_save, sender=get_user_model())
def codespace_post_save_handler(
    sender: type[get_user_model()], instance: get_user_model(), created: bool, **kwargs
) -> None:
    """
    This signal is used to send email to newly created
    user
    """

    if created:
        # send welcome email
        email_sender.delay(
            email_subject=f"Welcome {str(instance.first_name)}",
            email_to=str(instance.email),
            email_plaintext="emails/welcome.txt",
            email_template="emails/welcome.html",
            first_name=str(instance.first_name),
        )
