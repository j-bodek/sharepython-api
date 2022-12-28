from django.test import TestCase, SimpleTestCase
from django.contrib.auth import get_user_model
from core.models import CodeSpace, TmpCodeSpace
from unittest.mock import patch
import fakeredis
import uuid


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


class CodeSpaceModelTests(TestCase):
    """Test CodeSpace Model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )
        self.codespace = CodeSpace.objects.create(created_by=self.user)

    def test_redis_store_fields_attribute_is_dict(self):
        """Check if redis_store_fields was changed by metaclass
        from list to dict"""

        self.assertTrue(isinstance(CodeSpace.redis_store_fields, dict))

    @patch("core.signals.post_get.send")
    def test_on_get_post_get_signal_is_sent(self, patched_signal):
        """Test if on objects.get() post_get signal is sent"""

        CodeSpace.objects.get(uuid=self.codespace.uuid)
        self.assertTrue(patched_signal.called)
        self.assertEqual(patched_signal.call_count, 1)

    @patch("src.REDIS.hgetall", return_value={"name": "new_name", "code": "new_code"})
    def test_codespace_getattribute(self, patched_redis_hgetall):
        """Test if while getting field specified in redis_store_fields
        data from redis is returned"""

        self.assertEqual(self.codespace.code, "new_code")
        self.assertEqual(self.codespace.name, "new_name")


class TmpCodeSpaceTests(SimpleTestCase):
    """Test TmpCodeSpace"""

    def setUp(self):
        self.uuid = f"tmp-{str(uuid.uuid4())}"
        self.code = "tmp codespace code"

    @patch("core.manager.REDIS.exists", return_value=False)
    def test_tmpcodespace_doesnotexist_exception(self, patched_redis_exists):
        """Test if TmpCodeSpace can raise TmpCodeSpace.DoesNotExist"""

        with self.assertRaises(TmpCodeSpace.DoesNotExist):
            TmpCodeSpace.objects.get(uuid="invalid_uuid")

    @patch("core.models.codespace.REDIS")
    def test_tmpcodespace_save(self, patched_redis):
        """Test if on save TmpCodeSpace data is saved to redis"""
        r = fakeredis.FakeRedis(decode_responses=True)
        patched_redis.exists.return_value = False
        patched_redis.hmset.side_effect = r.hmset

        tmp_codespace = TmpCodeSpace(uuid=self.uuid, code=self.code)
        tmp_codespace.save()
        self.assertEqual(patched_redis.hmset.call_count, 1)
        data = r.hgetall(self.uuid) or {}
        self.assertEqual(data.get("code"), self.code)
        self.assertEqual(data.get("uuid"), self.uuid)

    @patch("core.models.codespace.REDIS.delete")
    def test_tmpcodespace_delete(self, patched_redis_delete):
        """Test if on delete TmpCodeSpace data is deleted to redis"""
        r = fakeredis.FakeRedis(decode_responses=True)
        r.hmset(self.uuid, {"uuid": self.uuid, "code": self.code})
        patched_redis_delete.side_effect = r.delete

        tmp_codespace = TmpCodeSpace(uuid=self.uuid, code=self.code)
        tmp_codespace.delete()
        self.assertEqual(r.hgetall(self.uuid), {})

    @patch("core.manager.REDIS")
    def test_tmpcodespace_objects_get(self, patched_redis):
        """Test if objects.get() return TmpCodeSpace instance"""
        patched_redis.exists.return_value = True
        patched_redis.hgetall.return_value = {
            "code": "mocked_code",
        }
        tmp_codespace = TmpCodeSpace.objects.get(uuid="mocked_uuid")
        self.assertEqual(tmp_codespace.uuid, "mocked_uuid")
        self.assertEqual(tmp_codespace.code, "mocked_code")
