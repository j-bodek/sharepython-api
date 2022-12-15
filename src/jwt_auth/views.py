from rest_framework import status, generics, permissions
from rest_framework.response import Response
from users.serializers import UserSerializer
from jwt_auth.permissions import IsNotAuthenticated
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Type


class TokenVerifyView(generics.GenericAPIView):
    """
    This View is used to verify if access token is still valid.
    It checks Authorization request header and returns 401 if token
    is invalid or 200 if it is valid
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Type[HttpRequest], *args, **kwargs) -> Type[Response]:
        return Response(data={}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    """
    This View is used to create new user and
    return access, refresh token and user data
    """

    serializer_class = UserSerializer
    token_class = RefreshToken
    permission_classes = (IsNotAuthenticated,)

    def create(self, request: Type[HttpRequest], *args, **kwargs) -> Type[Response]:
        """
        Validate data, create user instance, and return
        access, refresh token and user data
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # update serializer data with access and refresh token
        refresh = self.get_token(user)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": serializer.data,
        }

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(
        self, serializer: Type[UserSerializer]
    ) -> Type[get_user_model()]:
        return serializer.save()

    def perform_authentication(self, request):
        """
        Perform authentication lazily, the first time either
        `request.user` or `request.auth` is accessed.
        """
        pass

    @classmethod
    def get_token(cls, user: Type[get_user_model()]) -> Type[RefreshToken]:
        """Create and return refresh, access token"""
        return cls.token_class.for_user(user)
