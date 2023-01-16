from django.test import SimpleTestCase, RequestFactory
from unittest.mock import patch, MagicMock
from codespace.permissions import IsObjectOwner, IsCodeSpaceAccessTokenValid
import datetime


class TestIsObjectOwnerPermission(SimpleTestCase):
    """Test IsObjectOwnerPermission"""

    def setUp(self):
        self.permission = IsObjectOwner()
        self.owner = "owner"
        self.obj = MagicMock()
        self.obj.owner = self.owner

    def test_if_user_is_owner(self):
        """Permission should return True"""
        request = RequestFactory().get(path="/some_path/")
        request.user = self.owner
        self.assertTrue(
            self.permission.has_object_permission(request, MagicMock(), self.obj)
        )

    def test_if_user_is_not_owner(self):
        """Permission should return False"""
        request = RequestFactory().get(path="/some_path/")
        request.user = "not owner"
        self.assertFalse(
            self.permission.has_object_permission(request, MagicMock(), self.obj)
        )


class TestIsCodeSpaceAccessTokenValid(SimpleTestCase):
    """Test IsCodeSpaceAccessTokenValid"""

    def setUp(self):
        self.permission = IsCodeSpaceAccessTokenValid()
        self.request = RequestFactory().get(path="/some_path/")
        self.view = MagicMock()

    def create_timestamp(self, hours: int = 0):
        """Helper function to crate timestamp"""
        return datetime.datetime.timestamp(
            (datetime.datetime.now() + datetime.timedelta(hours=hours))
        )

    def test_with_invalid_token(self):
        """Permission should return False"""
        self.view.kwargs = {"token": "invalid_token"}
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    @patch("codespace.permissions.codespace_access_token_generator.decrypt_token")
    def test_with_expired_token(self, patched_decrypt_token):
        """Permission should return False"""

        patched_decrypt_token.return_value = (
            "codespace_uuid",
            self.create_timestamp(hours=-1),
        )
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    @patch("codespace.permissions.codespace_access_token_generator.decrypt_token")
    def test_with_valid_token(self, patched_decrypt_token):
        """Permission should return True"""

        patched_decrypt_token.return_value = (
            "codespace_uuid",
            self.create_timestamp(hours=1),
        )
        self.view.kwargs = {"token": "token"}
        self.view.codespace_uuid_kwarg_key = "uuid"
        self.assertTrue(self.permission.has_permission(self.request, self.view))
        self.assertEqual(self.view.kwargs.get("uuid"), "codespace_uuid")
