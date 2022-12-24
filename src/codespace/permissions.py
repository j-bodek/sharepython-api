from rest_framework import permissions


class IsObjectOwner(permissions.BasePermission):
    """
    Generic Permission that allows to check if request.user
    is object owner or not. Object owner field is determined
    by class attribute 'object_owner_field'
    """

    object_owner_field = "owner"

    def has_object_permission(self, request, view, obj):
        return getattr(obj, self.object_owner_field) == request.user


class IsCodeSpaceOwner(IsObjectOwner):
    """
    Permission used to check if request.user is
    codespace owner
    """

    object_owner_field = "created_by"
