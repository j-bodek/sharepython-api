from rest_framework import generics
from codespace.serializers import CodeSpaceSerializer, TmpCodeSpaceSerializer
from rest_framework.response import Response
from core.models import CodeSpace, TmpCodeSpace
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status


class CreateCodeSpaceView(generics.CreateAPIView):
    """View responsible for creating new codespace."""

    codespace_serializer_class = CodeSpaceSerializer
    tmp_codespace_serializer_class = TmpCodeSpaceSerializer

    def get_serializer_class(self):
        # if user is not authenticated create temporary codespace
        if self.request.user.is_authenticated:
            return self.codespace_serializer_class
        else:
            return self.tmp_codespace_serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RetrieveCodeSpaceView(generics.RetrieveAPIView):
    """View used to retrieve codespace data."""

    codespace_class = CodeSpace
    codespace_serializer_class = CodeSpaceSerializer

    tmp_codespace_class = TmpCodeSpace
    tmp_codespace_serializer_class = TmpCodeSpaceSerializer

    def get_serializer_class(self):
        """
        Return either codespace or tmp codespace
        serializer class
        """

        obj_uuid = self.kwargs.get("uuid", "")
        if obj_uuid.startswith("tmp-"):
            return self.tmp_codespace_serializer_class
        else:
            return self.codespace_serializer_class

    def get_object(self):
        obj_uuid = self.kwargs.get("uuid", "")
        if obj_uuid.startswith("tmp-"):
            try:
                return TmpCodeSpace.objects.get(uuid=obj_uuid)
            except TmpCodeSpace.DoesNotExist as e:
                raise Http404(e)
        else:
            return get_object_or_404(CodeSpace, uuid=obj_uuid)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
