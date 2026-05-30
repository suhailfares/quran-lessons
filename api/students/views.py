from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from quranlessons.roles import is_admin, resolve_create_teacher
from quranlessons.sync import SoftDeleteDestroyMixin, apply_sync_filter

from .models import Student
from .permissions import IsTeacher
from .serializers import StudentSerializer


@extend_schema(
    tags=["Students"],
    parameters=[
        OpenApiParameter(
            name="updated_since",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=False,
            description="ISO-8601 UTC. Returns only rows updated_at > updated_since (and includes tombstones).",
        ),
    ],
)
@extend_schema_view(
    create=extend_schema(
        description=(
            "Admins may include `teacher` (a teacher's user id) in the body to assign the "
            "new record to that teacher; non-admins always own what they create."
        ),
    ),
)
class StudentViewSet(SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = Student.objects.all() if is_admin(user) else Student.objects.filter(teacher=user)
        return apply_sync_filter(qs, self.request)

    def perform_create(self, serializer):
        serializer.save(teacher=resolve_create_teacher(self.request, serializer))

    def perform_update(self, serializer):
        student = self.get_object()
        if not is_admin(self.request.user) and student.teacher != self.request.user:
            raise PermissionDenied("You can only edit your own students.")
        serializer.save()

    def perform_destroy(self, instance):
        if not is_admin(self.request.user) and instance.teacher != self.request.user:
            raise PermissionDenied("You can only delete your own student.")
        super().perform_destroy(instance)
