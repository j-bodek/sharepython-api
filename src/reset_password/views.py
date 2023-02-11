from rest_framework import generics, status
from rest_framework.response import Response
from reset_password import serializers
from reset_password import signals


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
    - password - new password
    """


class ValidateResetPasswordView(generics.GenericAPIView):
    """
    This view is used to validate reset password token.
    It takes following post parameters:
    - token - reset password token
    """
