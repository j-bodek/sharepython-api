from django.db.models.signals import post_delete, post_save
from core.signals import post_get
from django.dispatch import receiver
from core.models import CodeSpace
from src import REDIS
from django.conf import settings


@receiver(post_delete, sender=CodeSpace)
def codespace_post_delete_handler(
    sender: type[CodeSpace], instance: CodeSpace, **kwargs
) -> None:
    """
    This signals is used to handle
    codespace deletion
    """

    # delete codespace from redis
    instance_uuid = str(instance.uuid)
    REDIS.delete(instance_uuid)


def save_codespace_data_to_redis(sender: type[CodeSpace], instance: CodeSpace) -> None:
    redis_key = str(getattr(instance, sender.redis_store_key))

    # if data for redis_key already exists
    # just update expiration time
    if not REDIS.exists(redis_key):
        redis_data = {
            str(key): str(getattr(instance, key))
            for key in sender.redis_store_fields.keys()
        }

        REDIS.hmset(redis_key, redis_data)

    # if data for codespace already stored in redis, extend expiration value
    REDIS.expire(redis_key, settings.CODESPACE_REDIS_EXPIRE_TIME)


@receiver(post_get, sender=CodeSpace)
def codespace_post_get_handler(
    sender: type[CodeSpace], instance: CodeSpace, **kwargs
) -> None:
    """
    This signals is used to set CodeSpace
    data in redis after geting specific CodeSpace
    from database
    """

    save_codespace_data_to_redis(sender, instance)


@receiver(post_save, sender=CodeSpace)
def codespace_post_save_handler(
    sender: type[CodeSpace], instance: CodeSpace, created: bool, **kwargs
) -> None:
    """
    This signals is used to set CodeSpace
    data in redis after creating new CodeSpace
    """

    if created:
        save_codespace_data_to_redis(sender, instance)
