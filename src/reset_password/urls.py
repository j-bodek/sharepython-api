from django.urls import path
from reset_password import views as reset_password_views

app_name = "reset_password"
urlpatterns = [
    path(
        "reset_password/request/",
        reset_password_views.RequestResetPasswordView.as_view(),
        name="reset_password_request",
    ),
    path(
        "reset_password/confirm/",
        reset_password_views.ConfirmResetPasswordView.as_view(),
        name="reset_password_confirm",
    ),
    path(
        "reset_password/validate/",
        reset_password_views.ValidateResetPasswordView.as_view(),
        name="reset_password_validate",
    ),
]
