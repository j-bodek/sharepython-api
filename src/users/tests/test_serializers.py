from django.test import TestCase
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer


class TestUserSerializer(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpwd123",
        )
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "test2@example.com",
        }
        self.serializer = UserSerializer

    def test_password_validation(self):
        """Test if password with less then 6
        characters or without digits is invalid"""

        self.user_data["password"] = "inv12"
        serializer = self.serializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())

        self.user_data["password"] = "invalid"
        serializer = self.serializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())

        self.user_data["password"] = "password123"
        serializer = self.serializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

    def test_update_password(self):
        """Test if password is updated properly"""

        serializer = self.serializer(
            instance=self.user,
            data={"password": "newpwd123"},
            partial=True,
        )
        serializer.is_valid()
        serializer.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpwd123"))
