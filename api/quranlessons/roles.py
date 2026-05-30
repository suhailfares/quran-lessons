"""Shared role helpers."""

# Roles that get elevated access across the API.
ADMIN_ROLES = ("admin", "manager")


def is_admin(user):
    """True for admin or manager — use for permission gates."""
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) in ADMIN_ROLES
    )


def is_strict_admin(user):
    """True only for role == 'admin' (not manager)."""
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) == "admin"
    )


def is_manager(user):
    """True only for role == 'manager'."""
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) == "manager"
    )


def same_mosque(user, mosque_name):
    """True if user's mosque_name matches the given value (both non-empty)."""
    user_mosque = getattr(user, "mosque_name", None)
    return bool(user_mosque and mosque_name and user_mosque == mosque_name)


def resolve_create_teacher(request, serializer):
    """Pick the owner for a new row.

    Admins and managers may supply a validated ``teacher`` via the request body
    (see ``TeacherAssignableSerializerMixin``). The mixin already validates that
    managers only assign teachers in their own mosque.
    """
    user = request.user
    if is_admin(user):
        return serializer.validated_data.get("teacher") or user
    return user
