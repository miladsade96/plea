import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from jwt import ExpiredSignatureError, InvalidSignatureError
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    GenericAPIView,
    DestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page

from accounts.models import CustomUser
from accounts.serializers import (
    UserRegistrationSerializer,
    ChangeUserPasswordSerializer,
    UserActivationResendSerializer,
    RequestResetForgottenPasswordEmailSerializer,
    ResetForgottenPasswordSerializer,
    UserInfoSerializer,
)
from accounts.tasks import send_account_activation_email, send_password_reset_email
from accounts.permissions import UserInfoPermission


class UserInfoRetrieveAPIView(RetrieveAPIView):
    model = CustomUser
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserInfoSerializer
    permission_classes = [UserInfoPermission]
    lookup_field = "username"

    @method_decorator(cache_page(timeout=60*60))
    @method_decorator(vary_on_headers("Authorization",))
    def get(self, request, *args, **kwargs):
        return super(UserInfoRetrieveAPIView, self).get(request, *args, **kwargs)


class UserRegistrationCreateAPIView(CreateAPIView):
    model = CustomUser
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            username = serializer.validated_data["username"]
            email = serializer.validated_data["email"]
            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            user = CustomUser.objects.get(username=username)
            token = self.generate_token_for_user(user)
            data = {
                "detail": "User created successfully. Check out your inbox to active your account.",
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
            }
            full_name = f"{first_name} {last_name}"
            sender = "account_activation@plea.org"
            send_account_activation_email.delay(token, sender, email, full_name)
            return Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def generate_token_for_user(user_obj):
        refresh = RefreshToken.for_user(
            user_obj,
        )
        return str(refresh.access_token)


class UserActivationAPIView(APIView):
    @staticmethod
    def get(request, token, *args, **kwargs):
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"details": "Token is not valid."}, status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_active:
            return Response({"detail": "User account is already active."})
        user.is_active = True
        user.save()
        return Response({"detail": "Your account activated successfully."})


class UserActivationResendAPIView(GenericAPIView):
    serializer_class = UserActivationResendSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            user = CustomUser.objects.get(email__iexact=email)
            full_name = f"{user.first_name} {user.last_name}"
            data = {"detail": "Activation email resend successfully."}
            token = self.generate_token_for_user(user)
            sender = "account_activation@plea.org"
            send_account_activation_email.delay(token, sender, email, full_name)
            return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def generate_token_for_user(user_obj):
        refresh = RefreshToken.for_user(
            user_obj,
        )
        return str(refresh.access_token)


class ChangeUserPasswordUpdateView(UpdateAPIView):
    model = CustomUser
    serializer_class = ChangeUserPasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.user_object = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if not self.user_object.check_password(
                serializer.validated_data["old_password"]
            ):
                return Response(
                    {"detail": "Old password was wrong!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.user_object.set_password(serializer.validated_data["new_password"])
            self.user_object.save()
            return Response(
                {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
            )


class RequestResetForgottenPasswordEmailAPIView(GenericAPIView):
    serializer_class = RequestResetForgottenPasswordEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            user = serializer.validated_data["user"]
            full_name = serializer.validated_data["full_name"]
            data = {"detail": "Password reset link sent successfully."}
            token = self.generate_token_for_user(user)
            sender = "reset_apssword@plea.org"
            send_password_reset_email.delay(token, sender, email, full_name)
            return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def generate_token_for_user(user_obj):
        refresh = RefreshToken.for_user(
            user_obj,
        )
        return str(refresh.access_token)


class ResetForgottenPasswordAPIView(UpdateAPIView):
    model = CustomUser
    serializer_class = ResetForgottenPasswordSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = jwt.decode(
                jwt=kwargs["token"], key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"details": "Token is not valid."}, status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(CustomUser, id=user_id)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        data = {"detail": "Password reset successfully."}
        return Response(data, status=status.HTTP_200_OK)


class CustomDiscardAuthTokenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteUserAccountDestroyAPIView(DestroyAPIView):
    queryset = CustomUser.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        obj = self.request.user
        obj.delete()
        data = {"detail": "User account deleted successfully."}
        return Response(data, status=status.HTTP_204_NO_CONTENT)
