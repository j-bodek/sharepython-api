from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from src import REDIS
from django.core.exceptions import ImproperlyConfigured
from core.manager import CodeSpaceManager, TmpCodeSpaceManager
from django.conf import settings
from django.core.exceptions import (
    ObjectDoesNotExist,
)


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
        "    else:\n"
        "        for i in range(0, n+1):\n"
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

    def __setattr__(self, name, value):
        """
        Override setattr method to also update data
        stored in redis
        """

        if name != "redis_store_fields" and name in self.redis_store_fields:
            self.__redis_setter(name, value)

        super().__setattr__(name, value)

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

    def __redis_setter(self, name, value):
        """
        Update key value stored in redis
        """

        key = str(getattr(self, self.redis_store_key))

        if (data := REDIS.hgetall(key)) and data.get(name):
            data[name] = value
            REDIS.hmset(key, data)
        else:
            return None

    def __redis_getter(self, name):
        """
        Try to return value stored in redis
        """

        key = str(getattr(self, self.redis_store_key))

        if data := REDIS.hgetall(key):
            return data.get(name)
        else:
            return None


class TmpCodeSpaceBase(type):
    """
    TmpCodeSpace metaclass
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        """
        In __new__ method set model attribute in class manager,
        set DoesNotExist exception
        """

        if not (manager := attrs.get("objects")):
            raise ImproperlyConfigured(f"{cls} must have 'objects' class attribute")

        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        # set manager model attribute
        manager.model = new_class
        module = attrs.get("__module__", "")

        # set DoesNotExist exception
        setattr(
            new_class,
            "DoesNotExist",
            models.base.subclass_exception(
                "DoesNotExist",
                (ObjectDoesNotExist,),
                module,
                attached_to=new_class,
            ),
        )

        return new_class


class TmpCodeSpace(object, metaclass=TmpCodeSpaceBase):
    """
    This class represents temporary codespace which
    is saved only in redis
    """

    objects = TmpCodeSpaceManager()
    redis_store_key = "uuid"
    redis_store_fields = ["code"]

    def __init__(self, uuid: str, code=None, *args, **kwargs) -> None:
        self.uuid = uuid
        self.code = code or get_default_code_value()

    def to_python(self) -> dict:
        """
        Returns dict representation of instance
        """

        data = {key: getattr(self, key) for key in self.redis_store_fields}
        data.update({self.redis_store_key: getattr(self, self.redis_store_key)})
        return data

    def save(self) -> None:
        """
        Used only once when creating new tmp codespace.
        If codespace edit nothing will happen
        """
        redis_key = str(getattr(self, self.redis_store_key))
        if not REDIS.exists(redis_key):
            REDIS.hmset(redis_key, self.to_python())

        REDIS.expire(redis_key, settings.TMP_CODESPACE_REDIS_EXPIRE_TIME)

    def delete(self) -> None:
        """
        Delete tmp codespace data from redis
        """

        redis_key = str(getattr(self, self.redis_store_key))
        REDIS.delete(redis_key)
