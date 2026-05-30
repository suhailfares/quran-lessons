from rest_framework.permissions import BasePermission

from quranlessons.roles import is_admin


class IsTeacher(BasePermission):
    """
        Allows access to users with role == 'teacher', or any admin-level user.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "role", None) == "teacher" or is_admin(user))
        )
