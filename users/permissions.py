from rest_framework.permissions import BasePermission


class IsNormal(BasePermission):
    """
    Allows access only to Normal users.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 'normal')


class IsAdmin(BasePermission):
    """
    Allows access only to Admin users or Django superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        ))



