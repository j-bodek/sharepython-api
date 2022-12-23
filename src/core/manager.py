from django.db import models
from core.query import CodeSpaceQuerySet
from src import REDIS


class CodeSpaceManager(models.manager.BaseManager.from_queryset(CodeSpaceQuerySet)):
    pass


class TmpCodeSpaceManager(object):
    """
    Custom TmpCodeSpace manager
    """

    def __init__(self, model=None):
        self.model = model

    def get(self, *args, **kwargs):
        """return TmpCodeSpace instance or raise DoesNotExist exception"""

        # redis store data as key:value so if uuid is not defined
        # we can't get value (does not exist error)
        if not (uuid := kwargs.get("uuid", "")) or not REDIS.exists(uuid):
            raise self.model.DoesNotExist("matching query does not exist.")

        data = REDIS.hgetall(uuid)
        # return model instance
        return self.model(uuid=uuid, **{str(k): str(v) for k, v in data.items()})
