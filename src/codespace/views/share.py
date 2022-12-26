from rest_framework import permissions, generics, status, exceptions
from rest_framework.response import Response
from codespace.permissions import IsCodeSpaceOwner, IsCodeSpaceAccessTokenValid
from codespace.serializers import TokenAccessCodeSpaceSerializer
from typing import Type


class TokenCodeSpaceAccessView(generics.GenericAPIView):
    """
    Takes codespace_uuid and expire_time (in seconds) and returns
    token that can be used to share codespace for specified time period
    """

    permission_classes = (permissions.IsAuthenticated, IsCodeSpaceOwner)
    serializer_class = TokenAccessCodeSpaceSerializer

    def post(self, request, *args, **kwargs) -> Type[Response]:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenCodeSpaceAccessVerifyView(generics.GenericAPIView):
    """
    This View is used to verify if codespace access token is still valid
    and returns 403 if token is invalid or 200 if it is valid
    """

    permission_classes = (IsCodeSpaceAccessTokenValid,)

    def post(self, request, *args, **kwargs) -> Type[Response]:
        return Response(data={}, status=status.HTTP_200_OK)

    def permission_denied(self, request, message=None, code=None) -> None:
        """
        Override this method to not raise NotAuthenticated since
        this view doesn't require authentication
        """

        raise exceptions.PermissionDenied(detail=message, code=code)
