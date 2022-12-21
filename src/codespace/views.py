from rest_framework import generics, status
from rest_framework.response import Response
from codespace.serializers import CodeSpaceSerializer


class CreateCodeSpaceView(generics.CreateAPIView):
    """View responsible for creating new codespace."""

    serializer_class = CodeSpaceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
