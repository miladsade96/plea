from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.views import (
    UserRegistrationCreateAPIView,
    UserActivationAPIView,
    ChangeUserPasswordUpdateView,
    UserActivationResendAPIView,
    RequestResetForgottenPasswordEmailAPIView,
    ResetForgottenPasswordAPIView,
    CustomDiscardAuthTokenAPIView,
    DeleteUserAccountDestroyAPIView,
    UserInfoRetrieveAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("user/<str:username>/", UserInfoRetrieveAPIView.as_view(), name="user_info"),
    path("registration/", UserRegistrationCreateAPIView.as_view(), name="registration"),
    path("delete/", DeleteUserAccountDestroyAPIView.as_view(), name="deletion"),
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
    # Token
    path("token/login/", ObtainAuthToken.as_view(), name="token_login"),
    path("token/logout/", CustomDiscardAuthTokenAPIView.as_view(), name="token_logout"),
    # JWT
    path("jwt/create/", TokenObtainPairView.as_view(), name="jwt_create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify"),
]
