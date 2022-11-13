import datetime
import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from jwt import ExpiredSignatureError, InvalidSignatureError
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    GenericAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from petition.models import Petition, Signature, Reason, Vote
from petition.paginations import PetitionDefaultPagination
from petition.permissions import IsOwnerOrIsAdminOrReadOnly
from petition.serializers import (
    PetitionListCreateSerializer,
    PetitionRetrieveUpdateDestroySerializer,
    SignatureListCreateSerializer,
    SignatureVerificationResendSerializer,
    ReasonListCreateSerializer,
    VoteCreateSerializer,
)
from petition.tasks import send_signature_verification_email


class PetitionListCreateAPIView(ListCreateAPIView):
    model = Petition
    queryset = Petition.objects.all()
    serializer_class = PetitionListCreateSerializer
    permission_classes = [IsOwnerOrIsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "owner__username": ["exact"],
    }
    search_fields = ["title", "description", "owner__username"]
    ordering_fields = ["created", "num_signatures", "goal"]
    pagination_class = PetitionDefaultPagination


class PetitionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    model = Petition
    queryset = Petition.objects.all()
    serializer_class = PetitionRetrieveUpdateDestroySerializer
    permission_classes = [IsOwnerOrIsAdminOrReadOnly]
    lookup_field = "slug"


class SignatureListCreateAPIView(ListCreateAPIView):
    model = Signature
    queryset = Signature.objects.filter(is_anonymous=False, is_verified=True)
    serializer_class = SignatureListCreateSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "petition__slug": ["icontains"],
        "country": ["icontains"],
        "city": ["icontains"],
    }
    search_fields = ["petition__slug", "email", "country", "city"]
    ordering_fields = ["created"]
    pagination_class = PetitionDefaultPagination
    lookup_field = ["petition__slug", "country", "city", "email"]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "detail": "Signature created successfully and verification email sent. Please verify your email"
                "in order to submit your signature on petition."
            }
            email = serializer.validated_data["email"]
            payload = {
                "first_name": serializer.validated_data["first_name"],
                "last_name": serializer.validated_data["last_name"],
                "email": email,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(hours=3),
            }
            token = jwt.encode(
                payload=payload, key=settings.SECRET_KEY, algorithm="HS256"
            )
            full_name = f"{payload.get('first_name')} {payload.get('last_name')}"
            sender = "signature_verification@plea.org"
            send_signature_verification_email.delay(token, sender, email, full_name)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignatureVerificationAPIView(APIView):
    @staticmethod
    def get(request, token, *args, **kwargs):
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            email = payload.get("email")
        except ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"details": "Token is not valid."}, status=status.HTTP_400_BAD_REQUEST
            )
        signature = get_object_or_404(Signature, email=email)
        if signature.is_verified:
            return Response(
                {"detail": "Signature is already verified and submitted on petition."}
            )
        signature.is_verified = True
        signature.save()
        return Response(
            {
                "detail": "Your signature verified and submitted on petition successfully."
            }
        )


class SignatureVerificationResendAPIView(GenericAPIView):
    serializer_class = SignatureVerificationResendSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        full_name = serializer.validated_data["full_name"]
        email = serializer.validated_data["email"]
        payload = {
            "full_name": full_name,
            "email": email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(hours=3),
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
        data = {"detail": "Signature verification email resend successfully."}
        send_signature_verification_email.delay(token, email, full_name)
        return Response(data, status=status.HTTP_200_OK)


class ReasonListCreateAPIView(ListCreateAPIView):
    model = Reason
    queryset = Reason.objects.all()
    serializer_class = ReasonListCreateSerializer
    permission_classes = [AllowAny]


class VoteListCreateAPIView(ListCreateAPIView):
    model = Vote
    queryset = Vote.objects.all()
    serializer_class = VoteCreateSerializer
    permission_classes = [AllowAny]
