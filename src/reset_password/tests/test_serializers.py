from django.test import SimpleTestCase
from unittest import mock
from reset_password import serializers as reset_pwd_serializers
from rest_framework import serializers


class TestRequestPasswordSerializer(SimpleTestCase):
    """Test RequestResetPasswordSerializer class"""

    def setUp(self):
        self.serializer_class = reset_pwd_serializers.RequestResetPasswordSerializer

    @mock.patch(
        "reset_password.serializers.RequestResetPasswordSerializer._RequestResetPasswordSerializer__check_user_exists",  # noqa
        return_value=False,
    )
    def test_is_valid_with_invalid_email(self, *mocks):
        """Expected to return ValidationError"""

        serializer = self.serializer_class(data={"email": "invalid@email.com"})

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    @mock.patch(
        "reset_password.serializers.RequestResetPasswordSerializer._RequestResetPasswordSerializer__check_user_exists",  # noqa
        return_value=True,
    )
    def test_is_valid_with_valid_email(self, *mocks):
        """Expect to return True"""

        serializer = self.serializer_class(data={"email": "valid@email.com"})
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data["email"], "valid@email.com")

    def test_generate_token_without_previously_called_is_valid(self):
        """AssertionError should be raised"""

        serializer = self.serializer_class(data={"email": "valid@email.com"})

        with self.assertRaises(AssertionError):
            serializer.generate_token()

    @mock.patch(
        "reset_password.serializers.RequestResetPasswordSerializer._RequestResetPasswordSerializer__get_user",  # noqa
    )
    @mock.patch(
        "reset_password.serializers.RequestResetPasswordSerializer.password_token_generator_class.make_token",  # noqa
    )
    def test_generate_token_with_previously_called_is_valid(
        self, mocked_make_token, *mocks
    ):
        """make_token method should be called on token_generator class"""

        serializer = self.serializer_class(data={"email": "valid@email.com"})
        setattr(serializer, "_validated_data", {"email": "valid@email.com"})
        mocked_make_token.return_value = "some_token"
        token = serializer.generate_token()

        mocked_make_token.assert_called_once()
        self.assertEqual(token, "some_token")

    def test_get_password_token_generator(self):
        """Instance of class that implement make_token method should be returned"""

        token_generator = self.serializer_class().get_password_token_generator()
        if not hasattr(token_generator, "make_token"):
            self.fail("Token generator class must implement 'make_token' method")
