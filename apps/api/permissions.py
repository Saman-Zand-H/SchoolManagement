from rest_framework import permissions


class CanCreate(permissions.BasePermission):
    """Gives access to users with permission to post"""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            return request.user.has_perm("supports.api_post")
        return False
