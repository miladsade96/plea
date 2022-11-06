from django.contrib import admin
from petition.models import Petition


class PetitionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "num_signatures", "goal")
    search_fields = ("title", "description", "owner__username")
    ordering = ("-created", "num_signatures", "goal")


admin.site.register(Petition, PetitionAdmin)
