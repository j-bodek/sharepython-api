from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    This serializer is used in TokenObtainPairView
    (while creating new access and refresh tokens)
    """

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        data.update(
            {
                "user": {
                    "uuid": self.user.uuid,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "email": self.user.email,
                }
            }
        )
        return data
