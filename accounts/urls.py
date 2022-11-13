from django.urls import path

from accounts.views import (
    UserRegistrationCreateAPIView,
    UserActivationAPIView,
    ChangeUserPasswordUpdateView,
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
        "change-password/",
        ChangeUserPasswordUpdateView.as_view(),
        name="change_user_password",
    ),
]
