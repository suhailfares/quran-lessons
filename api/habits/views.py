from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from habits.models import Habit, StudentPoints
from habits.permissions import IsTeacher
from habits.serializers import (
    HabitSerializer,
    StudentPointsSerializer,
)
from quranlessons.sync import SoftDeleteDestroyMixin, apply_sync_filter


SYNC_PARAM = OpenApiParameter(
    name="updated_since",
    type=OpenApiTypes.DATETIME,
    location=OpenApiParameter.QUERY,
    required=False,
    description="ISO-8601 UTC. Returns only rows updated_at > updated_since (and includes tombstones).",
)


@extend_schema(
    tags=["Habits"],
    summary="Manage Habits for current teacher",
    description="Habits CRUD restricted to the authenticated teacher.",
    parameters=[SYNC_PARAM],
)
class HabitViewSet(SoftDeleteDestroyMixin, ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = Habit.objects.all()

    def get_queryset(self):
        qs = Habit.objects.filter(teacher=self.request.user)
        return apply_sync_filter(qs, self.request)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


@extend_schema(
    tags=["Student Points"],
    parameters=[SYNC_PARAM],
)
class StudentPointsViewSet(
    SoftDeleteDestroyMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = StudentPointsSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = StudentPoints.objects.all()

    def get_queryset(self):
        qs = StudentPoints.objects.filter(teacher=self.request.user).select_related(
            "student", "habit", "lesson"
        )
        return apply_sync_filter(qs, self.request)

    def _validate_teacher_ownership(self, *, student, habit):
        user = self.request.user
        if student.teacher_id != user.id:  # type: ignore
            raise PermissionDenied("You can only award points to your own students.")
        if habit.teacher_id != user.id:  # type: ignore
            raise PermissionDenied("You can only use habits you created.")

    def perform_create(self, serializer):
        student = serializer.validated_data["student"]
        habit = serializer.validated_data["habit"]
        self._validate_teacher_ownership(student=student, habit=habit)

        serializer.save(teacher=self.request.user)
