from django.conf import settings
from typing import Tuple, Union
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import secrets


class CodeSpaceAccessToken(object):
    """
    Class that can be used to check/create codespace
    access token
    """

    @property
    def secret(self):
        """
        Return django secret key converted
        to 32 bytes
        """
        secret = hashlib.md5(settings.SECRET_KEY.encode("utf8")).hexdigest()
        secret = str.encode(secret)
        return secret

    def make_token(self, uuid: str, expire_time: int) -> str:
        """
        Create token using AES (Advanced Encryption Standard)
        algorithm
        """
        token_hash = self.__make_token_hash(uuid, expire_time)
        nonce = secrets.token_bytes(12)
        token = AESGCM(self.secret).encrypt(
            nonce=nonce,
            data=str.encode(token_hash),
            associated_data=b"",
        )
        return base64.urlsafe_b64encode(token)

    def decrypt_token(self, token: str) -> Union[Tuple[str, int], Tuple[None, None]]:
        """
        Return encrypted values (uuid, timestampe)
        """
        token = base64.urlsafe_b64decode(token.encode())
        return (
            AESGCM(self.secret)
            .decrypt(
                nonce=token[:12],
                data=token[12:],
                associated_data=b"",
            )
            .encode("utf8")
        )

    def __make_token_hash(self, uuid: str, expire_time: int) -> str:
        return f"{uuid}{str(expire_time)}"


codespace_access_token_generator = CodeSpaceAccessToken()
