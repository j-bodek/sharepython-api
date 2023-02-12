from rest_framework import generics, status
from rest_framework.response import Response
from reset_password import serializers
from users import serializers as users_serializers
from reset_password import signals
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


class RequestResetPasswordView(generics.GenericAPIView):
    """
    This view is used to send email request to reset password
    It takes following post parameters:
    - email - email of user that request reset password
    """

    request_password_reset_signal = signals.request_password_reset
    serializer_class = serializers.RequestResetPasswordSerializer

    def send_reset_password_requested_signal(
        self, serializer: serializers.RequestResetPasswordSerializer
    ) -> None:
        """Send request_password_reset_signal signal"""

        self.request_password_reset_signal.send(
            sender=self.__class__, serializer=serializer
        )

    def request_password_reset(self, request, *args, **kwargs) -> Response:
        """This method is used as post request handler"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.send_reset_password_requested_signal(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs) -> Response:
        return self.request_password_reset(request, *args, **kwargs)


class ConfirmResetPasswordView(generics.GenericAPIView):
    """
    This view is used to confirm password reset, and then set
    new user password.
    It takes following post parameters:
    - token - used to validate user
    - email - email of user that requested password reset
    - password - new password
    """

    token_serializer_class = serializers.RequestResetPasswordSerializer
    user_serializer_class = users_serializers.UserSerializer

    def get_user_serializer(self, **kwargs) -> users_serializers.UserSerializer:
        """Return instance of UserSerializer"""

        return self.user_serializer_class(**kwargs)

    def get_token_serializer(
        self, **kwargs
    ) -> serializers.RequestResetPasswordSerializer:
        """Return instance of UserSerializer"""

        return self.token_serializer_class(**kwargs)

    def get_object(self) -> get_user_model():
        """Return user with specified email"""

        return get_object_or_404(get_user_model(), email=self.request.data["email"])

    def validate_reset_password_token(self, request) -> None:
        """Check if provided token is valid, if not raise exception"""

        serializer = self.get_token_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

    def set_new_password(self, request) -> None:
        """Set new user password"""

        instance = self.get_object()
        serializer = self.get_user_serializer(
            instance=instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

    def perform_update(self, serializer) -> None:
        """Perform user password update"""

        serializer.save()

    def confirm_reset_password(self, request, *args, **kwargs) -> Response:
        """Handle confirm password reset"""

        self.validate_reset_password_token(request)
        self.set_new_password(request)
        return Response({}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs) -> Response:
        return self.confirm_reset_password(request, *args, **kwargs)


class ValidateResetPasswordView(generics.GenericAPIView):
    """
    This view is used to validate reset password token.
    It takes following post parameters:
    - token - reset password token
    - email - email of user that requested password reset
    """

    serializer_class = serializers.RequestResetPasswordSerializer

    def validate_reset_password_token(self, request, *args, **kwargs) -> Response:
        """Check if provieded valid token for user with given email"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs) -> Response:
        return self.validate_reset_password_token(request, *args, **kwargs)
