from rest_framework import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model


class RequestResetPasswordSerializer(serializers.Serializer):
    """
    Class used to validate data used to generate reset password request and
    generating token
    """

    password_token_generator_class = PasswordResetTokenGenerator

    # fields
    email = serializers.EmailField(required=True)
    # token field isn't required when user want to generate new token
    token = serializers.CharField(required=False)

    def validate_email(self, value: str) -> str:
        """Check if user with provided email exists"""

        if not self.__check_user_exists(email=value):
            raise serializers.ValidationError(
                f"User with email '{value}' does not exists"
            )

        return value

    def validate_token(self, value: str) -> str:
        """Check if provied token is valid for user with
        specified email"""

        # if token is empty string return it
        if value == "":
            return value

        try:
            user = self.__get_user(email=self.initial_data["email"])
        except get_user_model().DoesNotExist:
            """Validation error will be raised in validate_email method"""
            return ""

        if not self.get_password_token_generator().check_token(user, value):
            raise serializers.ValidationError(
                f"Provided token isn't valid for user with email '{self.initial_data['email']}'"  # noqa
            )

        return value

    def get_password_token_generator_class(self) -> type[PasswordResetTokenGenerator]:
        """Return class used to generate password reset token"""

        return self.password_token_generator_class

    def get_password_token_generator(
        self, *args, **kwargs
    ) -> PasswordResetTokenGenerator:
        """Retrun instance of PasswordResetTokenGenerator"""

        token_generator = self.get_password_token_generator_class()
        return token_generator(*args, **kwargs)

    def generate_token(self) -> str:
        """Generate reset password token for given email"""

        # Check if data was validated
        if not hasattr(self, "_validated_data"):
            msg = "Before generating token, validate data"
            raise AssertionError(msg)

        user = self.__get_user(email=self.validated_data["email"])
        token_generator = self.get_password_token_generator()
        return token_generator.make_token(user=user)

    def __check_user_exists(self, **kwargs) -> bool:
        """Check if user with given kwargs exists, Used for mocking in tests"""

        return get_user_model().objects.filter(**kwargs).exists()

    def __get_user(self, **kwargs) -> get_user_model():
        """Return user instance matching given kwargs, Used for mocking in tests"""

        return get_user_model().objects.get(**kwargs)
