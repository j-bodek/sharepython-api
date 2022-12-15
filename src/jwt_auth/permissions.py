from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """
    Allow access only to unauthenticated users.
    """

    def has_permission(self, request, view) -> bool:
        return not bool(request.user and request.user.is_authenticated)
