from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):
    """Test custom user model"""

    def setUp(self):
        self.email = "test@example.com"
        self.password = "testpassword123"

    def test_can_create_user(self):
        user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password,
        )
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(True not in [user.is_staff, user.is_superuser])

    def test_can_create_superuser(self):
        superuser = get_user_model().objects.create_superuser(
            email=self.email,
            password=self.password,
        )
        self.assertEqual(superuser.email, self.email)
        self.assertTrue(superuser.check_password(self.password))
        self.assertTrue(
            False not in [superuser.is_staff, superuser.is_superuser],
        )

    def test_cannnot_create_user_without_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password=self.password,
            )
