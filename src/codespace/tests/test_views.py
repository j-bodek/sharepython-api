from django.test import TestCase, SimpleTestCase
from unittest.mock import patch, Mock
from rest_framework.test import APIClient
from django.urls import reverse
import uuid
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from core.models import TmpCodeSpace, CodeSpace
from codespace.tokens import codespace_access_token_generator
import datetime
from typing import Type


class TestTokenCodeSpaceAccessCreateView(SimpleTestCase):
    """Test TokenCodeSpaceAccessCreateView"""

    def setUp(self):
        self.client = APIClient()

    @patch("codespace.views.share.IsCodeSpaceOwner.has_permission", return_value=True)
    @patch(
        "codespace.views.share.permissions.IsAuthenticated.has_permission",
        return_value=True,
    )
    def test_valid_post_request(self, *args):
        """Test if new token is returned after successfull request"""
        r = self.client.post(
            reverse("codespace:token_codespace_access"),
            data={"codespace_uuid": str(uuid.uuid4()), "expire_time": 120},
        )

        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data.get("token", False))


class TestTokenCodeSpaceAccessVerifyView(SimpleTestCase):
    """Test TokenCodeSpaceAccessVerifyView"""

    def setUp(self):
        self.client = APIClient()

    @patch(
        "codespace.views.share.IsCodeSpaceAccessTokenValid.has_permission",
        return_value=True,
    )
    def test_valid_token_request(self, *args):
        r = self.client.post(
            reverse("codespace:token_codespace_verify"), data={"token": "token"}
        )
        self.assertEqual(r.status_code, 200)

    @patch(
        "codespace.views.share.IsCodeSpaceAccessTokenValid.has_permission",
        return_value=False,
    )
    def test_invalid_token_request(self, *args):
        r = self.client.post(
            reverse("codespace:token_codespace_verify"), data={"token": "token"}
        )
        self.assertEqual(r.status_code, 403)


class TestCreateCodeSpaceView(TestCase):
    """Test CreateCodeSpaceView"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="test_password"
        )
        self.token = AccessToken().for_user(self.user)
        self.client = APIClient()

    @patch("codespace.serializers.CodeSpace.save")
    def test_with_codespace_model(self, patched_codespace_save):
        """Test with CodeSpace model"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        r = self.client.post(reverse("codespace:create_codespace"), data={})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(patched_codespace_save.call_count, 1)

    @patch("codespace.serializers.TmpCodeSpace.save")
    def test_with_tmp_codespace(self, patched_tmpcodespace_save):
        """Test with TmpCodeSpace"""
        r = self.client.post(reverse("codespace:create_codespace"), data={})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(patched_tmpcodespace_save.call_count, 1)


class TestRetrieveCodeSpaceView(TestCase):
    """Test RetrieveCodeSpaceView"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="test_password"
        )
        self.token = AccessToken().for_user(self.user)
        self.client = APIClient()

    @patch("codespace.views.codespace.TmpCodeSpace.objects.get")
    def test_retrieve_tmp_codespace(self, patched_objects_get):
        """Test retrieving data of tmp codespace"""

        codespace_uuid = f"tmp-{uuid.uuid4()}"
        patched_objects_get.return_value = TmpCodeSpace(
            uuid=codespace_uuid, code="test_code"
        )
        r = self.client.get(
            reverse("codespace:retrieve_codespace", kwargs={"uuid": codespace_uuid})
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get("uuid"), codespace_uuid)
        self.assertEqual(r.data.get("code"), "test_code")

    def test_retrieve_codespace(self):
        """Test retrieving data of codespace model"""

        codespace = CodeSpace.objects.create(created_by=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        r = self.client.get(
            reverse(
                "codespace:retrieve_codespace", kwargs={"uuid": str(codespace.uuid)}
            )
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get("uuid"), str(codespace.uuid))
        self.assertEqual(r.data.get("code"), str(codespace.code))

    def test_retrieve_codespace_without_permission(self):
        """Test retrieving data of codespace without either IsAuthenticated or IsOwner permission"""

        r = self.client.get(
            reverse("codespace:retrieve_codespace", kwargs={"uuid": str(uuid.uuid4())})
        )
        self.assertEqual(r.status_code, 401)


class TestCodeSpaceListView(TestCase):
    """Test CodeSpaceListView"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="test_password"
        )
        self.token = AccessToken().for_user(self.user)
        self.client = APIClient()

    def create_codespace(self, user: Type[get_user_model], **params) -> Type[CodeSpace]:
        """Helper function which create codespace"""
        return CodeSpace.objects.create(created_by=user, **params)

    def test_retrieve_codespaces_data(self):
        self.create_codespace(user=self.user)
        self.create_codespace(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        r = self.client.get(reverse("codespace:list_codespaces"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)


class TestRetrieveCodeSpaceAccessTokenView(TestCase):
    """Test RetrieveCodeSpaceAccessTokenView"""

    def setUp(self):
        self.token_generator = codespace_access_token_generator

    @patch("codespace.views.codespace.get_object_or_404")
    def test_with_valid_token(self, patched_get_object_or_404):
        """Test retrievieng codespace data with valid token"""
        codespace_uuid = uuid.uuid4()
        token = self.token_generator.make_token(codespace_uuid, 120)
        mocked_codespace_data = {
            "uuid": codespace_uuid,
            "name": "test_name",
            "code": "test_code",
            "created_by": "user",
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }
        mocked_codespace = Mock(spec=CodeSpace)
        for key, value in mocked_codespace_data.items():
            setattr(mocked_codespace, key, value)

        patched_get_object_or_404.return_value = mocked_codespace

        r = self.client.get(
            reverse(
                "codespace:retrieve_codespace_access_token", kwargs={"token": token}
            )
        )

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get("uuid"), str(codespace_uuid))
