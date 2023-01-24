from rest_framework import generics, permissions
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model


class RetrieveUpdateDestroyUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is used to update, delete and retrieve user instance
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self) -> get_user_model():
        """Return request.user"""

        return self.request.user
