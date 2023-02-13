from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient
from rest_framework import serializers
from django.urls import reverse
from unittest import mock
from reset_password import views as reset_pwd_views
from django.contrib.auth import get_user_model


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


class TestConfirmResetPasswordView(TestCase):
    """Test ConfirmResetPasswordView class"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="testuser@example.com", password="testpassword123"
        )
        self.view_class = reset_pwd_views.ConfirmResetPasswordView

    @mock.patch("reset_password.views.ConfirmResetPasswordView.get_token_serializer")
    def test_validate_reset_password_token(self, mocked_get_token_serializer):
        """Test if serializer.is_valid is called"""

        mocked_serializer = mock.MagicMock()
        mocked_get_token_serializer.return_value = mocked_serializer
        self.view_class().validate_reset_password_token(request=mock.MagicMock())
        mocked_serializer.is_valid.assert_called_once()

    @mock.patch(
        "reset_password.views.ConfirmResetPasswordView.validate_reset_password_token"
    )
    def test_with_valid_token(self, *mocks):
        """Test if 200 is returned and new password is set"""

        data = {
            "token": "some_token",
            "email": self.user.email,
            "password": "newpassword123",
        }
        r = self.client.patch(
            reverse("reset_password:reset_password_confirm"),
            data=data,
        )

        self.assertEqual(r.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data["password"]))

    @mock.patch(
        "reset_password.views.ConfirmResetPasswordView.validate_reset_password_token",
        side_effect=[serializers.ValidationError],
    )
    def test_with_invalid_token(self, *mocks):
        """Test if 400 is returned"""

        r = self.client.patch(
            reverse("reset_password:reset_password_confirm"),
            data={},
        )

        self.assertEqual(r.status_code, 400)


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
