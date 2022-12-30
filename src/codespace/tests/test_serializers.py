from django.test import SimpleTestCase
from rest_framework import serializers
from unittest.mock import patch, Mock
from codespace.serializers import (
    CodeSpaceSerializer,
    TmpCodeSpaceSerializer,
    TokenAccessCodeSpaceSerializer,
)
from core.models import TmpCodeSpace, CodeSpace
import uuid
import datetime


class TestCodeSpaceSerializer(SimpleTestCase):
    """Test CodeSpace Serializer"""

    def setUp(self):
        self.serializer = CodeSpaceSerializer
        self.uuid = str(uuid.uuid4())
        self.mocked_codespace_data = {
            "uuid": self.uuid,
            "name": "test_name",
            "code": "test_code",
            "created_by": "user",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }

    def test_with_fields_query_param(self):
        mocked_request = Mock()
        fields = ["uuid", "name"]
        mocked_request.query_params = {"fields": ",".join(fields)}

        mocked_codespace = Mock(spec=CodeSpace)
        for key, value in self.mocked_codespace_data.items():
            setattr(mocked_codespace, key, value)
        serializer = self.serializer(
            mocked_codespace, context={"request": mocked_request}
        )
        self.assertEqual(list(serializer.data.keys()), fields)
        self.assertEqual(serializer.data.get("uuid"), mocked_codespace.uuid)
        self.assertEqual(serializer.data.get("name"), mocked_codespace.name)

    def test_with_invalid_fields_query_param(self):
        mocked_request = Mock()
        fields = ["uuid", "name", "invalid_field"]
        mocked_request.query_params = {"fields": ",".join(fields)}

        mocked_codespace = Mock(spec=CodeSpace)
        for key, value in self.mocked_codespace_data.items():
            setattr(mocked_codespace, key, value)

        serializer = self.serializer(
            mocked_codespace, context={"request": mocked_request}
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.data


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
