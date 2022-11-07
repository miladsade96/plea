from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from petition.models import Petition, Signature
from petition.paginations import PetitionDefaultPagination
from petition.permissions import IsOwnerOrIsAdminOrReadOnly
from petition.serializers import (
    PetitionListCreateSerializer,
    PetitionRetrieveUpdateDestroySerializer,
    SignatureListCreateSerializer,
)


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
        "city": ["icontains"]
    }
    search_fields = ["petition__slug", "email", "country", "city"]
    ordering_fields = ["created"]
    pagination_class = PetitionDefaultPagination
    lookup_field = ["petition__slug", "country", "city", "email"]
