from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse


class TestTokenVerifyView(TestCase):
    """Test TokenVerifyView"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password123"
        )
        self.token = AccessToken.for_user(self.user)
        self.client = APIClient()

    def test_with_invalid_token(self):
        """expect to return 401"""

        res = self.client.get(reverse("token_verify"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_valid_token(self):
        """expect to return 200"""

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.get(reverse("token_verify"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestRegisterView(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password123"
        )
        self.valid_register_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "test2@example.com",
            "password": "password123",
        }
        self.token = AccessToken.for_user(self.user)
        self.client = APIClient()

    def test_authenticated_request(self):
        """Should return 403"""

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.post(reverse("register"), self.valid_register_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_request_data(self):
        """Should return 400"""

        res = self.client.post(
            reverse("register"),
            {"first_name": "John", "last_name": "Doe"},
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_request(self):
        """Should return 200, tokens and create new user"""

        res = self.client.post(
            reverse("register"),
            self.valid_register_data,
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
