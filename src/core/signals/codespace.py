from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.models import CodeSpace
from src import REDIS
from typing import Type


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
