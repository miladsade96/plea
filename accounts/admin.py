from django.contrib import admin
from accounts.models import CustomUser
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ("username", "email", "is_superuser", "is_active")
    list_filter = ("is_superuser", "is_active")
    search_fields = ("email", "username")
    ordering = ("-created_at",)


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
    def has_delete_permission(self, *args, **kwargs):
        return True


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(OutstandingToken)
admin.site.register(OutstandingToken, CustomOutstandingTokenAdmin)
