from django.urls import path
from petition.views import (
    PetitionListCreateAPIView,
    PetitionRetrieveUpdateDestroyAPIView,
)

app_name = "petition"

urlpatterns = [
    path("petition/", PetitionListCreateAPIView.as_view(), name="petition_list"),
    path(
        "petition/<slug:slug>/",
        PetitionRetrieveUpdateDestroyAPIView.as_view(),
        name="petition_detail",
    ),
]
