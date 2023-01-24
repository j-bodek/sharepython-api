from rest_framework.permissions import BasePermission
from django.http import HttpRequest
from django.views import View


class IsNotAuthenticated(BasePermission):
    """
    Allow access only to unauthenticated users.
    """

    def has_permission(self, request: HttpRequest, view: View) -> bool:
        """Return False if user is authenticated"""

        return not bool(request.user and request.user.is_authenticated)
