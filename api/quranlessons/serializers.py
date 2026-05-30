"""Shared serializer building blocks."""
from rest_framework import serializers

from quranlessons.roles import is_admin
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
        if "teacher" in attrs and not is_admin(getattr(request, "user", None)):
            attrs.pop("teacher")
        return attrs
