from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken


class TestRetrieveUpdateDestroyUserView(TestCase):
    """Test RetrieveUpdateDestroyUserView"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
        )
        self.token = AccessToken().for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_can_delete_user(self):
        """Test if view can delete user"""

        res = self.client.delete(reverse("retrieve_update_destroy_user"))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(email="test@example.com")

    def test_can_retrieve_user(self):
        """Test if can retrieve user data"""

        res = self.client.get(reverse("retrieve_update_destroy_user"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["uuid"], str(self.user.uuid))

    def test_can_update_user(self):
        """Test if can update user"""

        res = self.client.patch(
            reverse("retrieve_update_destroy_user"), {"first_name": "John"}
        )
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual("John", self.user.first_name)
