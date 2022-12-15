from django.test import TestCase
from django.contrib.auth import get_user_model
from jwt_auth.serializers import TokenObtainPairSerializer


class TestTokenObtainPairSerializer(TestCase):
    """
    Base TokenObtainPairSerializer class is provided by
    rest_framework_simplejwt so we will test only overwritten
    part
    """

    def setUp(self):
        self.serializer = TokenObtainPairSerializer
        self.email = "test@example.com"
        self.password = "password123"
        self.user = get_user_model().objects.create_user(
            email=self.email, password=self.password
        )

    def test_validated_data(self):
        """Test if in validated data user basic
        data is returned"""

        serializer = self.serializer(
            data={
                "email": self.email,
                "password": self.password,
            }
        )
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data["user"]["uuid"], self.user.uuid)
