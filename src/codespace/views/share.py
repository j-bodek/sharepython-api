from rest_framework import permissions, generics, status, exceptions
from rest_framework.response import Response
from django.http import HttpRequest, Http404
from core.models import CodeSpace
from codespace.permissions import IsCodeSpaceOwner
from codespace.serializers import TokenAccessCodeSpaceSerializer
from typing import Type


class TokenCodeSpaceAccessCreateView(generics.GenericAPIView):
    """
    Takes codespace_uuid, expire_time (in seconds), mode ["edit", "view_only"]
    and returns token that can be used to share codespace for specified time period
    """

    permission_classes = (permissions.IsAuthenticated, IsCodeSpaceOwner)
    serializer_class = TokenAccessCodeSpaceSerializer

    def get_object(self) -> CodeSpace:
        """
        Return CodeSpace object
        """

        try:
            obj = generics.get_object_or_404(
                CodeSpace, uuid=self.request.data.get("codespace_uuid")
            )
        except Http404:
            raise exceptions.NotFound(detail="CodeSpace does not exists")

        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request: HttpRequest, *args, **kwargs) -> Type[Response]:
        """Create and return access and refresh tokens"""

        # raise 404 if not exists or permission denied if not owner
        self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
