from django.db.models.query import QuerySet
from core.signals import post_get
from django.db.models import Model


class CodeSpaceQuerySet(QuerySet):
    """
    Custom QuerySet class which send 'post_get'
    signal every time get method is called
    """

    def get(self, *args, **kwargs) -> Model:
        instance = super().get(*args, **kwargs)
        # send post get signal
        post_get.send(sender=type(instance), instance=instance)
        return instance
