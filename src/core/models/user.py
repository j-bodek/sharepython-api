from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
import uuid
from django.db import models
from typing import Union
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.humanize.templatetags import humanize


class UserManager(BaseUserManager):
    """
    This class is used to define custom user manager
    that create user with email as first positional argument
    """

    def _create_user(
        self,
        email: str,
        password: Union[str, None] = None,
        **extra_fields,
    ):
        """
        Create and save user with given email and password
        """

        email = self.normalize_email(email)
        if not email:
            raise ValueError("Email value must be set")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: Union[str, None] = None,
        **extra_fields,
    ):
        extra_fields.update({"is_staff": False, "is_superuser": False})
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: Union[str, None] = None,
        **extra_fields,
    ):
        extra_fields.update({"is_staff": True, "is_superuser": True})
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that don't have unique username
    but unique email, and uuid as pk
    """

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    uuid = models.UUIDField(
        primary_key=True,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
    email = models.EmailField(
        _("email"),
        max_length=255,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(_("first_name"), max_length=255, blank=True)
    last_name = models.CharField(_("last_name"), max_length=255, blank=True)
    is_staff = models.BooleanField(
        _("is_staff"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),  # noqa
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # override default user manager
    objects = UserManager()

    @property
    def last_login_humanize(self):
        """returns humanized last login date"""
        return humanize.naturaltime(self.last_login)

    @property
    def date_joined_humanize(self):
        """returns humanized join date"""
        return humanize.naturaltime(self.date_joined)
