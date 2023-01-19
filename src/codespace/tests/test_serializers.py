from django.test import SimpleTestCase
from rest_framework import serializers
from unittest.mock import patch, Mock
from codespace.serializers import (
    CodeSpaceSerializer,
    CodeSpaceTokenSerializer,
    TmpCodeSpaceSerializer,
    TokenAccessCodeSpaceSerializer,
)
from core.models import TmpCodeSpace, CodeSpace
import uuid
import datetime


def get_mocked_codespace_data(uuid: str) -> dict:
    """
    Helper function used to create mocked codespace data
    """

    return {
        "uuid": uuid,
        "name": "test_name",
        "code": "test_code",
        "created_by": "user",
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }


class TestCodeSpaceSerializer(SimpleTestCase):
    """Test CodeSpace Serializer"""

    def setUp(self):
        self.serializer = CodeSpaceSerializer
        self.uuid = str(uuid.uuid4())
        self.mocked_codespace_data = get_mocked_codespace_data(self.uuid)

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


class TestCodeSpaceTokenSerializer(SimpleTestCase):
    """
    Test CodeSpaceTokenSerializer class
    """

    def setUp(self):
        self.serializer = CodeSpaceTokenSerializer
        self.uuid = str(uuid.uuid4())
        self.mocked_codespace_data = get_mocked_codespace_data(self.uuid)

    def test_if_mode_is_added_to_validated_data(self):
        """Test if mode value is present in validated data"""

        mocked_codespace = Mock(spec=CodeSpace)
        for key, value in self.mocked_codespace_data.items():
            setattr(mocked_codespace, key, value)
        serializer = self.serializer(
            mocked_codespace,
            data={},
            context={
                "request": Mock(query_params={"fields": "uuid,mode"}),
                "view": Mock(kwargs={"mode": "view_only"}),
            },
        )
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.data["mode"], "view_only")


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

    def setUp(self):
        self.serializer = TokenAccessCodeSpaceSerializer
        self.codespace_uuid = uuid.uuid4()

    @patch("codespace.serializers.codespace_access_token_generator.make_token")
    def test_get_token_without_mode(self, patched_make_token):
        """Test if validation error will be raised"""
        serializer = self.serializer(
            data={"codespace_uuid": self.codespace_uuid, "expire_time": 120}
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    @patch("codespace.serializers.codespace_access_token_generator.make_token")
    def test_get_token_with_invalid_mode(self, patched_make_token):
        """Test if validation error will be raised"""

        serializer = self.serializer(
            data={
                "codespace_uuid": self.codespace_uuid,
                "expire_time": 120,
                "mode": "invalid_mode",
            }
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    @patch(
        "codespace.serializers.codespace_access_token_generator.make_token",
        return_value="token",
    )
    def test_get_token_with_valid_mode(self, patched_make_token):
        """Test if token will be created successfully"""

        for i, mode in enumerate(self.serializer._declared_fields["mode"].choices, 1):

            serializer = self.serializer(
                data={
                    "codespace_uuid": self.codespace_uuid,
                    "expire_time": 120,
                    "mode": mode,
                }
            )

            serializer.is_valid(raise_exception=True)
            self.assertEqual(patched_make_token.call_count, i)
            patched_make_token.assert_called_with(self.codespace_uuid, 120, mode)
            self.assertEqual(serializer.validated_data.get("token"), "token")
