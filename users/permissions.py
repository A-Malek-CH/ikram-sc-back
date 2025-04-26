from rest_framework.permissions import BasePermission

class IsNormal(BasePermission):
    """
    Allows access only to Normal users.
    """

    def has_permission(self, request, view):
        return bool(request.user.role == 'normal')

class IsAdmin(BasePermission):
    """
    Allows access only to Admins.
    """

    def has_permission(self, request, view):
        return bool(request.user.role == 'admin')

class IsPremuim(BasePermission):
    """
    Allows access only to Premium users.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_premium)