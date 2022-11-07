from django.urls import path
from petition.views import (
    PetitionListCreateAPIView,
    PetitionRetrieveUpdateDestroyAPIView,
    SignatureListCreateAPIView,
)

app_name = "petition"

urlpatterns = [
    path("petition/", PetitionListCreateAPIView.as_view(), name="petition_list"),
    path(
        "petition/<slug:slug>/",
        PetitionRetrieveUpdateDestroyAPIView.as_view(),
        name="petition_detail",
    ),
    path("signature/", SignatureListCreateAPIView.as_view(), name="signature_list"),
]
