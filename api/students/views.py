from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

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
class StudentViewSet(SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_queryset(self):
        qs = Student.objects.filter(teacher=self.request.user)
        return apply_sync_filter(qs, self.request)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def perform_update(self, serializer):
        student = self.get_object()
        if student.teacher != self.request.user:
            raise PermissionDenied("You can only edit your own students.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.teacher != self.request.user:
            raise PermissionDenied("You can only delete your own student.")
        super().perform_destroy(instance)
