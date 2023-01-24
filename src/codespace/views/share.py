from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.http import HttpRequest
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

    def post(self, request: HttpRequest, *args, **kwargs) -> Type[Response]:
        """Create and return access and refresh tokens"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
