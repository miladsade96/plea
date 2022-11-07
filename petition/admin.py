from django.contrib import admin
from petition.models import Petition, Signature


class PetitionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "num_signatures", "goal")
    search_fields = ("title", "description", "owner__username")
    ordering = ("-created", "num_signatures", "goal")


class SignatureAdmin(admin.ModelAdmin):
    list_display = (
        "petition",
        "first_name",
        "last_name",
        "email",
        "country",
        "city",
        "postal_code",
        "let_me_know",
        "is_anonymous",
        "is_verified",
    )
    search_fields = ("petition__slug", "email", "country", "city")
    ordering = ("created",)
    list_filter = ("country", "city")


admin.site.register(Petition, PetitionAdmin)
admin.site.register(Signature, SignatureAdmin)
