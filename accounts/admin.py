from django.contrib import admin
from accounts.models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ("username", "email", "is_superuser", "is_active")
    list_filter = ("is_superuser", "is_active")
    search_fields = ("email", "username")
    ordering = ("-created_at",)


admin.site.register(CustomUser, CustomUserAdmin)
