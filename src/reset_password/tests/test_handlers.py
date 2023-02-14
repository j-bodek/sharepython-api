from django.test import SimpleTestCase
from django.conf import settings
from unittest import mock
from reset_password.handlers import request_password_reset_handler


class TestRequestPasswordResetHandler(SimpleTestCase):
    """
    Test request_password_reset_handler function
    """

    def setUp(self):
        self.handler_func = request_password_reset_handler

    @mock.patch("reset_password.handlers.reset_password.email_sender")
    def test_if_email_sender_called(self, mocked_email_sender):
        """Test if email_sender.delay is called with expected arguments"""

        mocked_serializer = mock.MagicMock()
        mocked_serializer.generate_token.return_value = "some_token"
        mocked_serializer.validated_data = {"email": "someemail@gmail.com"}
        self.handler_func(sender=mock.Mock(), serializer=mocked_serializer)

        # test if send email_sender task was called
        mocked_email_sender.delay.assert_called_once()
        args, kwargs = mocked_email_sender.delay.call_args

        # test email_sender task call arguments
        self.assertEqual(kwargs["email_to"], mocked_serializer.validated_data["email"])
        self.assertEqual(
            kwargs["reset_password_url"],
            settings.RESET_PASSWORD_URL(
                token="some_token", email="someemail@gmail.com"
            ),
        )
