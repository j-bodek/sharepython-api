from django.test import SimpleTestCase
from rest_framework.test import APIClient
from rest_framework import serializers
from django.urls import reverse
from unittest import mock
from reset_password import views as reset_pwd_views


class TestRequestResetPasswordView(SimpleTestCase):
    """Test RequestResetPasswordView class"""

    def setUp(self):
        self.client = APIClient()
        self.view_class = reset_pwd_views.RequestResetPasswordView

    @mock.patch(
        "reset_password.views.RequestResetPasswordView.send_reset_password_requested_signal"  # noqa
    )
    @mock.patch("reset_password.views.RequestResetPasswordView.get_serializer")
    def test_request_password_reset(
        self, mocked_get_serializer, mocked_send_reset_password_requested_signal
    ):
        """
        Test if serializer is_valid and send_reset_password_request_signal are called
        """

        data = {"email": "someemail@gmail.com"}

        mocked_serializer = mock.MagicMock(data=data)
        mocked_get_serializer.return_value = mocked_serializer

        r = self.client.post(
            reverse("reset_password:reset_password_request"),
            data=data,
        )

        mocked_send_reset_password_requested_signal.assert_called_once_with(
            mocked_serializer
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["email"], data["email"])

    @mock.patch(
        "reset_password.views.RequestResetPasswordView.request_password_reset_signal"
    )
    def test_send_reset_password_requested_signal(
        self, mocked_request_password_reset_signal
    ):
        """Test if request_password_reset_signal is send"""

        mocked_serializer = mock.MagicMock()
        self.view_class().send_reset_password_requested_signal(
            serializer=mocked_serializer
        )

        mocked_request_password_reset_signal.send.assert_called_once_with(
            sender=self.view_class, serializer=mocked_serializer
        )


class TestValidateResetPasswordView(SimpleTestCase):
    """Test ValidateResetPasswordView class"""

    def setUp(self):
        self.client = APIClient()

    @mock.patch("reset_password.views.ValidateResetPasswordView.get_serializer")
    def test_with_invalid_token(self, mocked_get_serializer):
        """Test if response with status 400 is returned"""

        mocked_serializer = mock.MagicMock()
        mocked_serializer.is_valid.side_effect = [serializers.ValidationError]
        mocked_get_serializer.return_value = mocked_serializer

        data = {"email": "test@example.com", "token": "invalid_token"}
        r = self.client.post(
            reverse("reset_password:reset_password_validate"),
            data=data,
        )

        self.assertEqual(r.status_code, 400)

    @mock.patch("reset_password.views.ValidateResetPasswordView.get_serializer")
    def test_with_valid_token(self, mocked_get_serializer):
        """Test if response with status 200 is returned"""

        data = {"email": "test@example.com", "token": "valid_token"}
        mocked_serializer = mock.MagicMock(data=data)
        mocked_get_serializer.return_value = mocked_serializer

        r = self.client.post(
            reverse("reset_password:reset_password_validate"),
            data=data,
        )

        self.assertEqual(r.status_code, 200)
