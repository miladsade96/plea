from django.urls import path

from accounts.views import UserRegistrationCreateAPIView, UserActivationAPIView

app_name = "accounts"

urlpatterns = [
    path("registration/", UserRegistrationCreateAPIView.as_view(), name="registration"),
    path(
        "activation/confirm/<str:token>/",
        UserActivationAPIView.as_view(),
        name="activation",
    ),
]
