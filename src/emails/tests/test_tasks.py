from django.test import SimpleTestCase
from unittest import mock
from emails.tasks import EmailSender


class TestEmailSender(SimpleTestCase):
    """
    Class used to test EmailSender celery task
    """

    def setUp(self):
        # initialize task
        self.email_sender = EmailSender()

    @mock.patch("emails.tasks.EmailMultiAlternatives")
    @mock.patch("emails.tasks.EmailSender._EmailSender__update_message_content")
    @mock.patch("emails.tasks.EmailSender._EmailSender__send_message")
    def test_run_method(
        self,
        mocked_email_multi_alternatives,
        mocked_update_message_content,
        mocked_send_message,
    ):
        """
        Test if update_message_content and send_message methods are called
        correctly
        """
        kwargs = {
            "email_subject": "email_subject",
            "email_to": "email_to",
            "email_plaintext": "email_plaintext",
            "email_template": "email_template",
        }
        self.email_sender.run(**kwargs)
        mocked_email_multi_alternatives.assert_called_once()
        mocked_update_message_content.assert_called_once()
        mocked_send_message.assert_called_once()

    @mock.patch("emails.tasks.logging.error")
    def test_on_failure_method(self, mocked_logging_error):
        """
        Test if logging error is called
        """

        self.email_sender.on_failure(
            BaseException, task_id=0, args=(), kwargs={}, einfo="einfo"
        )
        mocked_logging_error.assert_called_once()

    def __get_mocked_render(self, return_value):
        """Return mocked get_template().render()"""

        return mock.MagicMock(render=mock.MagicMock(return_value=return_value))

    @mock.patch("emails.tasks.get_template")
    def test_update_message_content_without_plain_text(self, mocked_get_template):
        """
        Test if context added through attach_alternative method
        """

        contents = [["folder/template.html", "text/html"]]
        mocked_get_template.return_value = self.__get_mocked_render(
            return_value="some_content"
        )
        MockedMessage = mock.Mock()
        self.email_sender._EmailSender__update_message_content(
            message=MockedMessage, contents=contents
        )

        self.assertEqual(MockedMessage.body.call_count, 0)
        MockedMessage.attach_alternative.assert_called_once_with(
            "some_content", "text/html"
        )

    @mock.patch("emails.tasks.get_template")
    def test_update_message_content_with_plain_text(self, mocked_get_template):
        """
        Test if message body set to content
        """

        contents = [["folder/template.txt", "text/plain"]]
        mocked_get_template.return_value = self.__get_mocked_render(
            return_value="some_content"
        )
        MockedMessage = mock.Mock()
        self.email_sender._EmailSender__update_message_content(
            message=MockedMessage, contents=contents
        )

        self.assertEqual(MockedMessage.attach_alternative.call_count, 0)
        self.assertEqual(MockedMessage.body, "some_content")

    def test_get_contents(self):
        """
        Test if list of text/plain, text/html contents are returned
        """

        contents = self.email_sender._EmailSender__get_contents(
            email_plaintext="email_plaintext", email_template="email_template"
        )
        self.assertEqual(
            contents,
            [
                ["email_plaintext", "text/plain"],
                ["email_template", "text/html"],
            ],
        )

    def test_send_message(self):
        """
        Test if message.send is called
        """

        MockedMessage = mock.Mock()
        self.email_sender._EmailSender__send_message(message=MockedMessage)
        MockedMessage.send.assert_called_once()
