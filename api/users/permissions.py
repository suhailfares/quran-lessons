from rest_framework.permissions import BasePermission

from quranlessons.roles import is_admin


class IsTeacher(BasePermission):
    """Allows access to users with role == 'teacher', or any admin-level user."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "role", None) == "teacher" or is_admin(user))
        )


class IsAdmin(BasePermission):
    """Allows access to admin-level users (admin or manager)."""

    def has_permission(self, request, view):
        return is_admin(request.user)


class IsStrictAdmin(BasePermission):
    """Allows access only to users with role == 'admin' (not manager)."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )
