import django.dispatch

"""
This file is used to define custom signals
"""


# This signal is used when CodeSpace is 'get' from database
post_get = django.dispatch.Signal()
