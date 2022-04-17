from rest_framework import permissions


class CanCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            return request.user.has_perm("api_can_post")
        return False
