from django.urls import path
from petition.views import (
    PetitionListCreateAPIView,
    PetitionRetrieveUpdateDestroyAPIView,
    SignatureListCreateAPIView,
    SignatureVerificationAPIView,
    SignatureVerificationResendAPIView,
    ReasonListCreateAPIView,
    VoteListCreateAPIView,
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
    path(
        "signature/verification/confirm/<str:token>/",
        SignatureVerificationAPIView.as_view(),
        name="signature_verification_confirm",
    ),
    path(
        "signature/verification/resend/",
        SignatureVerificationResendAPIView.as_view(),
        name="signature_verification_resend",
    ),
    path("reason/", ReasonListCreateAPIView.as_view(), name="reason_list"),
    path("vote/", VoteListCreateAPIView.as_view(), name="vote"),
]
