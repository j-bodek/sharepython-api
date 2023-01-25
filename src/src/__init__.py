from .redis import REDIS
from .celery import app as CELERY_APP

# import redis instance to __init__ file to ensures
# that it will be loaded when django starts
__all__ = ("REDIS", "CELERY_APP")
