from django.conf import settings
from typing import Type, Tuple, Union
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import secrets
from datetime import datetime, timedelta


class CodeSpaceAccessToken:
    """
    Class that can be used to check/create codespace
    access token
    """

    @property
    def __secret(self) -> bytes:
        """
        Return django secret key hashed using sha256
        as 32 bytes
        """
        secret = hashlib.sha256(settings.SECRET_KEY.encode("utf8")).digest()
        return secret

    def make_token(self, uuid: str, expire_time: int, mode: str) -> str:
        """
        Create token using AES (Advanced Encryption Standard)
        algorithm. It takes following arguments:
        - uuid - codespace uuid
        - expire_time - time for which token will be valid
        - mode - share mode (edit, view_only)
        """
        token_hash = self.__make_token_hash(uuid, expire_time, mode)
        nonce = secrets.token_bytes(12)
        token = nonce + AESGCM(self.__secret).encrypt(
            nonce=nonce,
            data=str.encode(token_hash),
            associated_data=b"",
        )
        b64_token = base64.urlsafe_b64encode(token)
        return b64_token.decode()

    def decrypt_token(self, token: str) -> Union[Tuple[str, int], Tuple[None, None]]:
        """
        Return encrypted values (uuid, timestampe)
        """
        token = base64.urlsafe_b64decode(token.encode())
        decrypted_token = AESGCM(self.__secret).decrypt(token[:12], token[12:], b"")
        return decrypted_token.decode("utf8").split(":")

    def __make_token_hash(self, uuid: str, expire_time: int, mode: str) -> str:
        return f"{uuid}:{str(self._expire_ts(expire_time))}:{mode}"

    def _expire_ts(self, expire_time: int) -> int:
        """
        Return expire date timestamp
        """

        expire_date = self._now() + timedelta(seconds=expire_time)
        timestamp = int(datetime.timestamp(expire_date))
        return timestamp

    def _now(self) -> Type[datetime]:
        """This method will be used for mocking in tests"""
        return datetime.now()


codespace_access_token_generator = CodeSpaceAccessToken()
