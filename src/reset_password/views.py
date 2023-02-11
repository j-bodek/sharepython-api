from rest_framework import generics, permissions
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model


class RequestResetPasswordView(generics.GenericAPIView):
    """
    This view is used to send email request to reset password
    It takes following post parameters:
    - email - email of user that request reset password
    """


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
