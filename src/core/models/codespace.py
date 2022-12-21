from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from datetime import datetime
from django.utils.translation import gettext_lazy as _


class CodeSpace(models.Model):
    """
    Class used to store user code space informations
    """

    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        max_length=36,
    )
    name = models.CharField(
        _("name"),
        default=lambda: datetime.now().strftime("%b %d %I:%M %p"),
        max_length=255,
        blank=False,
        null=False,
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="created_codespaces",
    )
    shared_with = models.ManyToManyField(
        get_user_model(),
        related_name="shared_codespaces",
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
