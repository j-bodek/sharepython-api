from rest_framework import generics, permissions
from users.serializers import UserSerializer


class RetrieveUpdateDestroyUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is used to update, delete and retrieve user instance
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
