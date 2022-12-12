from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import Type


class UserSerializer(serializers.ModelSerializer):
    """Serialize User Model"""

    class Meta:
        model = get_user_model()
        fields = (
            "uuid",
            "first_name",
            "last_name",
            "password",
            "email",
        )
        read_only_fields = ["uuid"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 6,
            }
        }

    def validate_password(self, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )

        return value

    def create(self, valid_data: dict) -> Type[get_user_model()]:
        """Create and return new user instance"""

        return get_user_model().objects.create_user(**valid_data)
