from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from core.manager import CodeSpaceManager, TmpCodeSpaceManager
from django.conf import settings
from src import REDIS
import uuid


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
            # check if class has attribute named field
            if field not in attrs:
                raise ImproperlyConfigured(
                    f"{cls} class don't have '{field}' attribute"
                )

            redis_store_fields[field] = True

        # If redis_store_key inside redis_store_fields
        # __getattribute__ method will cause infinite recursion
        if redis_store_key in redis_store_fields:
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
    Class used to store user code space informations.
    On
    """

    redis_store_key = "uuid"
    # list of fields that will be stored in redis
    redis_store_fields = ["name", "code"]
    # list of fields that after setattribute will be changed in redis
    # this will be used to prevent from updating code value by serializers
    # value for code should be updated ONLY through websocket endpoint!
    redis_settable_fields = ["name"]

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

    @classmethod
    def is_cached_in_redis(cls, uuid: str) -> bool:
        """
        Check if codespace data is cached in redis
        """

        return REDIS.exists(uuid)

    @classmethod
    def save_redis_changes(cls, codespace) -> None:
        """
        This method is used to update postgres codespace data
        with data stored in redis
        """

        uuid = str(codespace.uuid)
        if not cls.is_cached_in_redis(uuid):
            raise ObjectDoesNotExist("Can not find CodeSpace data in cache")

        data = REDIS.hmget(uuid, *cls.redis_store_fields)
        data = {k: v for k, v in zip(cls.redis_store_fields, data)}
        codespace.__dict__.update(**data)
        codespace.save()

    def __setattr__(self, name, value):
        """
        Override setattr method to also update data
        stored in redis
        """

        if (
            name != "redis_store_fields"
            and name in self.redis_settable_fields
            and name in self.redis_store_fields
        ):
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
            and (value := self.__redis_getter(name)) is not None
        ):
            return value

        return super().__getattribute__(name)

    def __redis_setter(self, name, value):
        """
        Update hash value stored in redis
        """

        key = str(getattr(self, self.redis_store_key))

        if REDIS.hexists(key, name):
            REDIS.hset(key, name, value)
        else:
            return None

    def __redis_getter(self, name):
        """
        Try to retrieve hash value stored in redis
        """

        key = str(getattr(self, self.redis_store_key))

        if (value := REDIS.hget(key, name)) is not None:
            return value
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

        # set DoesNotExist exception
        setattr(
            new_class,
            "DoesNotExist",
            models.base.subclass_exception(
                "DoesNotExist",
                (ObjectDoesNotExist,),
                attrs.get("__module__", ""),
                attached_to=new_class,
            ),
        )

        return new_class


class TmpCodeSpace(object, metaclass=TmpCodeSpaceBase):
    """
    This class represents temporary codespace which
    is saved only in redis. Temporary codespace can be created
    by anonymous user
    """

    objects = TmpCodeSpaceManager()
    redis_store_key = "uuid"
    redis_store_fields = ["code"]

    def __init__(self, uuid: str, code=None, *args, **kwargs) -> None:
        self.uuid = uuid
        self.code = code if code is not None else get_default_code_value()

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
