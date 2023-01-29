import celery
import logging
from typing import Union
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from src import CELERY_APP


class EmailSender(celery.Task):
    """
    This Task is used to send emails asynchronously in
    celery worker.
    """

    def run(
        self,
        email_subject: str,
        email_to: str,
        email_plaintext: str,  # specify txt file with email content
        email_template: Union[None, str] = None,  # specify email html template
        **context,  # any additional kwargs will be treated as email context
    ) -> None:
        """This method should define body of the task executed by workers"""

        message = EmailMultiAlternatives(
            email_subject,
            email_from=settings.DEFAULT_FROM_EMAIL,
            to=[email_to],
        )

        self.__update_message_content(
            message=message,
            contents=self.__get_contents(email_plaintext, email_template),
            **context,
        )

        self.__send_message(message)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """This method is called when task fails"""

        logging.error(
            f"{task_id} failed: {exc}\n",
            f"Failed to send email to '{kwargs.get('email_to')}'\n",
        )

    def __update_message_content(
        self,
        message: EmailMultiAlternatives,
        contents: list[
            list[str]
        ],  # list defining contents [[template_name, conent_type]]
        **context,
    ) -> None:
        """This method is used to update EmailMultiAlternatives instance content
        in place"""

        for template, content_type in contents:
            content = get_template(template).render(context)
            if content_type == "text/plain":
                message.body = content
            else:
                message.attach_alternatives(content, content_type)

    def __get_contents(
        self, email_plaintext: str, email_template: str
    ) -> list[list[str]]:
        """This method is used to create list of email contents"""

        return [
            [email_plaintext, "text/plain"],
            [email_template, "text/html"],
        ]

    def __send_message(self, message: EmailMultiAlternatives) -> None:
        """this method is used to send email message"""

        message.send()


email_sender = CELERY_APP.register_task(EmailSender())
