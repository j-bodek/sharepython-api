from rest_framework import status, generics, permissions
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer


class RetrieveUpdateDestroyUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is used to update, delete and retrieve user instance
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    lookup_url_kwarg = "uuid"
