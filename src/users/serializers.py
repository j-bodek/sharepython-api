from rest_framework import serializers
from django.contrib.auth import get_user_model


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
        """Minimum requirements for passwords are 6 or more characters,
        at least one digit"""

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        return value

    def create(self, valid_data: dict) -> get_user_model():
        """Create and return new user instance"""

        return get_user_model().objects.create_user(**valid_data)

    def update(
        self, instance: get_user_model(), validated_data: dict
    ) -> get_user_model():
        """
        Overrider update method to set updated password properly
        """

        for key, value in validated_data.items():
            if key == "password":
                self.__update_password(instance, value)
            else:
                setattr(instance, key, value)

        instance.save()
        return instance

    def __update_password(self, user: get_user_model(), password: str) -> None:
        """This method is used to set password with user set_password method"""

        user.set_password(password)
