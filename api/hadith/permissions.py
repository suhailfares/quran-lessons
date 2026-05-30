from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    """
        Allows access to users with role == 'teacher', or any admin.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, "role", None) in ("teacher", "admin")
