"""Shared serializer building blocks."""
from rest_framework import serializers

from quranlessons.roles import is_strict_admin, is_manager, same_mosque
from users.models import User


# Exposes a writable, admin-only `teacher` field for assigning ownership. The
# field is rendered in the request schema (so it shows up in Swagger), but it is
# only honoured for admins. For non-admins the field is dropped during validation
# and the view assigns ownership to the requesting user.
# A concrete serializer's `Meta.fields` must include "teacher" and must NOT list
# it in `read_only_fields`.
class TeacherAssignableSerializerMixin(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="teacher"),
        required=False,
        help_text=(
            "Admins only: id of the teacher to own this record. Ignored for "
            "non-admins, who always become the owner of what they create."
        ),
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if "teacher" not in attrs:
            return attrs
        if is_strict_admin(user):
            pass  # unrestricted
        elif is_manager(user):
            teacher = attrs["teacher"]
            if not same_mosque(user, getattr(teacher, "mosque_name", None)):
                raise serializers.ValidationError(
                    {"teacher": "You can only assign to teachers in your mosque."}
                )
        else:
            attrs.pop("teacher")  # non-elevated users cannot assign ownership
        return attrs
