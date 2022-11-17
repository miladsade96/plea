from django.urls import path

from accounts.views import (
    UserRegistrationCreateAPIView,
    UserActivationAPIView,
    ChangeUserPasswordUpdateView,
    UserActivationResendAPIView,
    RequestResetForgottenPasswordEmailAPIView,
    ResetForgottenPasswordAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("registration/", UserRegistrationCreateAPIView.as_view(), name="registration"),
    path(
        "activation/confirm/<str:token>/",
        UserActivationAPIView.as_view(),
        name="activation",
    ),
    path(
        "activation/resend/",
        UserActivationResendAPIView.as_view(),
        name="activation_resend",
    ),
    path(
        "change-password/",
        ChangeUserPasswordUpdateView.as_view(),
        name="change_user_password",
    ),
    path(
        "reset-password/",
        RequestResetForgottenPasswordEmailAPIView.as_view(),
        name="reset_password_request",
    ),
    path(
        "reset-password/confirm/<str:token>/",
        ResetForgottenPasswordAPIView.as_view(),
        name="reset_password_confirm",
    ),
]
