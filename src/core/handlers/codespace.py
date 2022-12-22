from django.db.models.signals import post_delete
from core.signals import post_get
from django.dispatch import receiver
from core.models import CodeSpace
from src import REDIS
from typing import Type
from django.conf import settings


@receiver(post_delete, sender=CodeSpace)
def codespace_post_delete_handler(
    sender: CodeSpace, instance: Type[CodeSpace], **kwargs
):
    """
    This signals is used to handle
    codespace deletion
    """

    # delete codespace from redis
    instance_uuid = str(instance.uuid)
    REDIS.delete(instance_uuid)


@receiver(post_get, sender=CodeSpace)
def codespace_post_get_handler(sender: CodeSpace, instance: Type[CodeSpace], **kwargs):
    """
    This signals is used to set CodeSpace
    data in redis after geting specific CodeSpace
    from database
    """

    redis_key = str(getattr(instance, sender.redis_store_key))

    # if data for redis_key already exists
    # just update expiration time
    if not REDIS.exists(redis_key):
        redis_data = {
            key: str(getattr(instance, key)) for key in sender.redis_store_fields.keys()
        }

        REDIS.hmset(redis_key, redis_data)

    REDIS.expire(redis_key, settings.CODESPACE_REDIS_EXPIRE_TIME)
