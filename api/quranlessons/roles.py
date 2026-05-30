"""Shared role helpers."""


def is_admin(user):
    """True if the user is authenticated and has the admin role."""
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) == "admin"
    )


def resolve_create_teacher(request, serializer):
    """Pick the owner (`teacher`) to stamp on a newly created row.

    Admins may supply a validated ``teacher`` to assign the row to that teacher
    (see ``TeacherAssignableSerializerMixin``). Non-admins, and admins who omit
    it, own the row themselves. The mixin already drops ``teacher`` for
    non-admins, so reading ``validated_data`` here is safe.
    """
    user = request.user
    if is_admin(user):
        return serializer.validated_data.get("teacher") or user
    return user
