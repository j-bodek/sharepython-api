from rest_framework import serializers
from core.models import CodeSpace
from src import REDIS
import uuid
import pickle
from typing import Type, Union
from django.contrib.auth.models import AbstractBaseUser


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
        else:
            # if user is not authenticated set
            # codespace as temporary
            instance_uuid = f"tmp-{uuid.uuid4()}"

        data = pickle.dumps(self.get_redis_data())
        REDIS.set(instance_uuid, data)
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
