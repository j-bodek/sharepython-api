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

    def validate_email(self, value: str) -> str:
        """Check if user with provided email exists"""

        if not get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError(
                f"User with email '{value}' does not exists"
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

        user = get_user_model().objects.get(email=self.validated_data["email"])
        token_generator = self.get_password_token_generator()
        return token_generator.make_token(user=user)
