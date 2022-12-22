from rest_framework import generics
from codespace.serializers import CodeSpaceSerializer, TmpCodeSpaceSerializer
from rest_framework.response import Response
from core.models import CodeSpace
from django.shortcuts import get_object_or_404


class CreateCodeSpaceView(generics.CreateAPIView):
    """View responsible for creating new codespace."""

    codespace_serializer_class = CodeSpaceSerializer
    tmp_codespace_serializer_class = TmpCodeSpaceSerializer

    # @TODO add tmp_codespace_serializer
    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return self.codespace_serializer_class
        else:
            return self.tmp_codespace_serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RetrieveCodeSpaceView(generics.RetrieveAPIView):
    """View used to retrieve codespace data."""

    model_class = CodeSpace
    serializer_class = CodeSpaceSerializer

    def get_object(self):
        obj_uuid = self.kwargs.get("uuid", "")
        return get_object_or_404(CodeSpace, uuid=obj_uuid)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
