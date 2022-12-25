from rest_framework import permissions, generics, status
from rest_framework.response import Response
from codespace.permissions import IsCodeSpaceOwner
from codespace.serializers import TokenAccessCodeSpaceSerializer


class TokenCodeSpaceShareView(generics.GenericAPIView):
    """
    Takes codespace_uuid and expire_time (in seconds) and returns
    token that can be used to share codespace for specified time period
    """

    permission_classes = (permissions.IsAuthenticated, IsCodeSpaceOwner)
    serializer_class = TokenAccessCodeSpaceSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
