from django.test import SimpleTestCase
from unittest.mock import patch
from codespace.serializers import TmpCodeSpaceSerializer, TokenAccessCodeSpaceSerializer
from core.models import TmpCodeSpace
import uuid


class TestTmpCodeSpaceSerializer(SimpleTestCase):
    """Test TmpCodeSpaceSerializer"""

    def test_uuid_with_tmp_prefix(self):
        """Test if uuid with 'tmp' prefix raises exception"""
        serializer = TmpCodeSpaceSerializer(data={})
        serializer.is_valid(raise_exception=True)
        self.assertTrue(serializer.validated_data.get("uuid").startswith("tmp-"))

    @patch("codespace.serializers.TmpCodeSpace.save")
    def test_can_create(self, patched_tmpcodespace_save):
        """Test if can create TmpCodeSpace using TmpCodeSpaceSerializer"""

        serializer = TmpCodeSpaceSerializer(data={})
        serializer.is_valid(raise_exception=True)
        tmp_codespace = serializer.save()
        self.assertTrue(isinstance(tmp_codespace, TmpCodeSpace))
        self.assertEqual(patched_tmpcodespace_save.call_count, 1)


class TestTokenAccessCodeSpaceSerializer(SimpleTestCase):
    """Test TokenAccessCodeSpaceSerializer"""

    @patch(
        "codespace.serializers.codespace_access_token_generator.make_token",
        return_value="token",
    )
    def test_add_token(self, patched_make_token):
        codespace_uuid = uuid.uuid4()
        serializer = TokenAccessCodeSpaceSerializer(
            data={"codespace_uuid": codespace_uuid, "expire_time": 120}
        )
        serializer.is_valid(raise_exception=True)
        self.assertEqual(patched_make_token.call_count, 1)
        patched_make_token.assert_called_with(codespace_uuid, 120)
        self.assertEqual(serializer.validated_data.get("token"), "token")
