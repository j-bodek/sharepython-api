from django.test import SimpleTestCase
from codespace.tokens import codespace_access_token_generator
from datetime import datetime, timedelta
from unittest.mock import patch


class TestCodeSpaceAccessToken(SimpleTestCase):
    """Test CodeSpaceAccessToken Class"""

    def setUp(self):
        self.cur_datetime = datetime.now()
        self.uuid = "test_uuid"
        self.expire_time = 120
        self.mode = "view_onlye"
        self.token_generator = codespace_access_token_generator

    def create_timestamp(self, seconds: int = 0):
        return datetime.timestamp(self.cur_datetime + timedelta(seconds=seconds))

    @patch("codespace.tokens.CodeSpaceAccessToken._now")
    def test_can_encrypt_decrypt_token(self, patched_now):
        patched_now.return_value = self.cur_datetime
        token = self.token_generator.make_token(self.uuid, self.expire_time, self.mode)
        self.assertNotEqual(token, self.uuid)
        self.assertNotEqual(token, self.expire_time)

        uuid, expire_timestamp, mode = self.token_generator.decrypt_token(token)
        self.assertEqual(uuid, self.uuid)
        self.assertEqual(
            int(expire_timestamp),
            int(self.create_timestamp(self.expire_time)),
        )
        self.assertEqual(mode, self.mode)
