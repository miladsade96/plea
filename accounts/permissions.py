from rest_framework.permissions import IsAuthenticated


class UserInfoPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.username == request.user.username or request.user.is_staff is True:
            return True
        return False
