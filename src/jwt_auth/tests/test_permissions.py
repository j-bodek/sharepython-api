from django.test import SimpleTestCase
from unittest.mock import MagicMock
from jwt_auth.permissions import IsNotAuthenticated


class TestIsNotAuthenticated(SimpleTestCase):
    """Test IsNotAuthenticated Permission"""

    def setUp(self):
        self.permission = IsNotAuthenticated()
        self.request = MagicMock(user=MagicMock())
        self.view = MagicMock()

    def test_with_authenticated(self):
        """Test with authenticated request"""

        self.request.user.is_authenticated = True
        self.assertFalse(
            self.permission.has_permission(self.request, self.view),
        )

    def test_with_not_authenticated(self):
        """Test with not authenticated request"""

        self.request.user.is_authenticated = False
        self.assertTrue(
            self.permission.has_permission(self.request, self.view),
        )
