from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from src import REDIS
from django.db.models.query import QuerySet
from django.core.exceptions import ImproperlyConfigured
from core.signals import post_get


def get_default_code_value() -> str:
    """
    Return default code snippet displayed
    when user creates new code space
    """

    return str(
        "def fibonacci(n):\n\n"
        "    a, b = 0, 1\n"
        "    if n < 0:\n"
        "        yield 'Incorrect input'\n"
        "    elif n <= 1:\n"
        "        yield n\n"
        "    else:\n"
        "        for i in range(1, n+1):\n"
        "            yield a\n"
        "            a, b = b, a + b\n\n"
        "for i in fibonacci(10):\n"
        "   print(i)\n"
    )


def get_default_name():
    """
    Return default codespace name,
    Before Django 1.7 could use lambda
    """

    return datetime.now().strftime("%b %d %I:%M %p")


class CodeSpaceBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        """
        Before class initialization validate redis_store_key
        and redis_store_fields
        """

        redis_store_key = attrs.get("redis_store_key")
        redis_store_fields = {}
        for field in attrs.get("redis_store_fields"):
            if not attrs.get(field):
                raise ImproperlyConfigured(
                    f"{cls} class don't have '{field}' attribute"
                )

            redis_store_fields[field] = True

        # If redis_store_key inside redis_store_fields
        # __getattribute__ method will cause infinite recursion
        if redis_store_fields.get(redis_store_key):
            raise ImproperlyConfigured(
                str(
                    f"redis_store_key named '{redis_store_key}' "
                    "can't be included inside redis_store_fields"
                )
            )

        # change redis_store_fields from list to dict
        # in order to get O(1) time complexity when checking
        # if name inside redis_store_fields (__getattribute__ method)
        attrs.update({"redis_store_fields": redis_store_fields})

        return super().__new__(cls, name, bases, attrs, **kwargs)


class CodeSpaceQuerySet(QuerySet):
    """
    Custom QuerySet class which send 'post_get'
    signal every time get method is called
    """

    def get(self, *args, **kwargs):
        instance = super().get(*args, **kwargs)
        post_get.send(sender=type(instance), instance=instance)
        return instance


class CodeSpaceManager(models.manager.BaseManager.from_queryset(CodeSpaceQuerySet)):
    pass


class CodeSpace(models.Model, metaclass=CodeSpaceBase):
    """
    Class used to store user code space informations
    """

    redis_store_key = "uuid"
    redis_store_fields = ["name", "code"]
    objects = CodeSpaceManager()

    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        max_length=36,
    )
    name = models.CharField(
        _("name"),
        default=get_default_name,
        max_length=255,
        blank=False,
        null=False,
    )
    code = models.TextField(
        _("code"),
        default=get_default_code_value,
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="created_codespaces",
    )
    created_at = models.DateTimeField(
        _("date created"),
        default=datetime.now,
        editable=False,
    )
    updated_at = models.DateTimeField(
        _("date updated"),
        auto_now=True,
    )

    def __getattribute__(self, name):
        """
        Override gettattribute method to return value
        from redis for specified fields
        """

        if (
            name != "redis_store_fields"
            and name in self.redis_store_fields
            and (value := self.__redis_getter(name))
        ):
            return value

        return super().__getattribute__(name)

    def __redis_getter(self, name):
        """
        Try to return value saved in redis
        """

        key = str(getattr(self, self.redis_store_key))
        if data := REDIS.hgetall(key):
            return data.get(name)
        else:
            return None
