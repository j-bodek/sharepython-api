from .redis import REDIS

# import redis instance to __init__ file to ensures
# that it will be loaded when django starts
__all__ = ("REDIS",)
