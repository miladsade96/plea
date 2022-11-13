import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from jwt import ExpiredSignatureError, InvalidSignatureError
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from accounts.serializers import UserRegistrationSerializer
from accounts.tasks import send_account_activation_email


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
