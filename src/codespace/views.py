from rest_framework import generics
from codespace.serializers import CodeSpaceSerializer


class CreateCodeSpaceView(generics.CreateAPIView):
    """View responsible for creating new codespace."""

    serializer_class = CodeSpaceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
