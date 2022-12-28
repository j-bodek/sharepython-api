from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from core.models import CodeSpace
from core.handlers.codespace import save_codespace_data_to_redis
from django.db.models.signals import post_delete, post_save
from core.signals import post_get
import fakeredis


class TestCodeSpaceHandlers(SimpleTestCase):
    """Test codespace signals handlers"""

    @patch("core.handlers.codespace.REDIS.delete")
    def test_codespace_post_delete_handler(self, patched_redis_delete):
        """Test if REDIS.delete is called after codespace post_delete signal"""
        MockInstance = MagicMock()
        MockInstance.uuid = "mocked_uuid"
        post_delete.send(sender=CodeSpace, instance=MockInstance)
        self.assertEqual(1, patched_redis_delete.call_count)
        patched_redis_delete.assert_called_with("mocked_uuid")

    @patch("core.handlers.codespace.REDIS")
    def test_save_codespace_data_to_redis(self, patched_redis):
        """Test if data is saved to redis after calling save_codespace_data_to_redis"""
        r = fakeredis.FakeRedis(decode_responses=True)
        patched_redis.exists.return_value = False
        patched_redis.hmset.side_effect = r.hmset
        patched_redis.expire.side_effect = r.expire
        MockInstance = MagicMock()
        MockInstance.uuid = "mocked_uuid"
        MockInstance.name = "mocked_name"
        MockInstance.code = "mocked_code"

        save_codespace_data_to_redis(sender=CodeSpace, instance=MockInstance)
        data = r.hgetall("mocked_uuid") or {}
        self.assertEqual(data.get("name"), "mocked_name")
        self.assertEqual(data.get("code"), "mocked_code")

    @patch("core.handlers.codespace.save_codespace_data_to_redis")
    def test_codespace_post_get_handler(self, patched_save_codespace_data_to_redis):
        """Test if save_codespace_data_to_redis after codespace post_get"""
        post_get.send(sender=CodeSpace, instance="test_instance")
        self.assertEqual(patched_save_codespace_data_to_redis.call_count, 1)
        patched_save_codespace_data_to_redis.assert_called_with(
            CodeSpace, "test_instance"
        )

    @patch("core.handlers.codespace.save_codespace_data_to_redis")
    def test_codespace_post_save_handler(self, patched_save_codespace_data_to_redis):
        """Test if save_codespace_data_to_redis after creating new codespace"""
        post_save.send(sender=CodeSpace, instance="test_created_instance", created=True)
        post_save.send(
            sender=CodeSpace, instance="test_updated_instance", created=False
        )
        self.assertEqual(patched_save_codespace_data_to_redis.call_count, 1)
        patched_save_codespace_data_to_redis.assert_called_with(
            CodeSpace, "test_created_instance"
        )
