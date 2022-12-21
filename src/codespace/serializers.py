from rest_framework import serializers
from core.models import CodeSpace
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from typing import Type, Union
from src import REDIS
import uuid
import pickle


class CodeSpaceSerializer(serializers.ModelSerializer):
    """Serialize CodeSpace Model"""

    class Meta:
        model = CodeSpace
        fields = (
            "uuid",
            "name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uuid",
            "created_at",
            "updated_at",
        )

    def save(
        self, user: Type[AbstractBaseUser], **kwargs
    ) -> Union[Type[CodeSpace], None]:
        """
        User is positional argument representing user
        that create codespace
        """

        # if user is authenticated perform default
        # save
        if user.is_authenticated:
            super().save(created_by=user, **kwargs)
        else:
            self.instance = None

        # add codespace to redis
        return self.save_to_redis()

    def save_to_redis(self) -> None:
        """
        This function is used to save codespace to
        redis
        """

        if self.instance is not None:
            instance_uuid = str(self.instance.uuid)
            expire_time = settings.CODESPACE_REDIS_EXPIRE_TIME
        else:
            # if user is not authenticated set
            # codespace as temporary
            instance_uuid = f"tmp-{uuid.uuid4()}"
            expire_time = settings.TMP_CODESPACE_REDIS_EXPIRE_TIME

        data = pickle.dumps(self.get_redis_data())
        REDIS.set(instance_uuid, data, ex=expire_time)
        # update _data pseudo private variable
        # it will be returned by data property method
        self._data = {"uuid": instance_uuid}

        return self.instance

    def get_redis_data(self) -> dict:
        """
        Return data that redis will store as
        value to codespace uuid
        """

        return {
            "code": "",
        }
