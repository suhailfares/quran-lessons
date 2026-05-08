from datetime import datetime, time, timezone as dt_timezone
from http import HTTPStatus

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action

from habits.models import Habit, StudentPoints
from habits.permissions import IsTeacher
from habits.serializers import (
    HabitSerializer,
    StudentPointsSerializer,
    StudentPointsBatchPayloadSerializer,
    StudentPointsBatchResponseSerializer,
)
from lessons.models import Lesson
from quranlessons.sync import SoftDeleteDestroyMixin, apply_sync_filter
from students.models import Student


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
        is_minus = serializer.validated_data.get("isMinus", False)
        self._validate_teacher_ownership(student=student, habit=habit)

        points = -habit.minusPoints if is_minus else habit.points

        serializer.save(
            teacher=self.request.user,
            points=points,
        )

    @extend_schema(
        summary="Batch overwrite daily student-point totals",
        description=(
            "Overwrites all StudentPoints rows for each (student, habit, day) tuple "
            "with absolute plus_count/minus_count totals. Idempotent — safe for re-sync."
        ),
        request=StudentPointsBatchPayloadSerializer,
        responses={201: StudentPointsBatchResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="batch")
    def batch(self, request, *args, **kwargs):
        payload = StudentPointsBatchPayloadSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        date_value = payload.validated_data["date"]
        lesson_id = payload.validated_data.get("lesson_id")
        entries = payload.validated_data["entries"]

        user = request.user

        lesson = None
        if lesson_id is not None:
            try:
                lesson = Lesson.objects.get(pk=lesson_id, teacher=user)
            except Lesson.DoesNotExist:
                raise ValidationError({"lesson_id": "Lesson not found or not yours."})

        student_ids = {e["student_id"] for e in entries}
        habit_ids = {e["habit_id"] for e in entries}
        students = {s.id: s for s in Student.objects.filter(id__in=student_ids, teacher=user)}
        habits = {h.id: h for h in Habit.objects.filter(id__in=habit_ids, teacher=user)}

        missing_students = sorted(student_ids - set(students.keys()))
        missing_habits = sorted(habit_ids - set(habits.keys()))
        if missing_students:
            raise ValidationError({"entries": f"Students not yours/missing: {missing_students}"})
        if missing_habits:
            raise ValidationError({"entries": f"Habits not yours/missing: {missing_habits}"})

        stamp = datetime.combine(date_value, time(12, 0, 0), tzinfo=dt_timezone.utc)

        deleted_total = 0
        written_total = 0
        with transaction.atomic():
            for entry in entries:
                student = students[entry["student_id"]]
                habit = habits[entry["habit_id"]]

                deleted, _ = StudentPoints.objects.filter(
                    teacher=user,
                    student=student,
                    habit=habit,
                    created_at__date=date_value,
                ).delete()
                deleted_total += deleted

                rows = []
                for _ in range(entry["plus_count"]):
                    rows.append(StudentPoints(
                        teacher=user, student=student, habit=habit,
                        lesson=lesson, isMinus=False, points=habit.points,
                        created_at=stamp,
                    ))
                for _ in range(entry["minus_count"]):
                    rows.append(StudentPoints(
                        teacher=user, student=student, habit=habit,
                        lesson=lesson, isMinus=True, points=-habit.minusPoints,
                        created_at=stamp,
                    ))
                if rows:
                    StudentPoints.objects.bulk_create(rows)
                    written_total += len(rows)

        return Response(
            {"written": written_total, "deleted": deleted_total},
            status=HTTPStatus.CREATED,
        )
