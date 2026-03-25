from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from habits.models import Habit, StudentPoints
from habits.permissions import IsTeacher
from habits.serializers import HabitSerializer, StudentPointsSerializer


# Create your views here.

@extend_schema(
    tags=["Habits"],
    summary="Manage Habits for current teacher",
    description="Habits CRUD restricted to the authenticated teacher."
)
class HabitViewSet(ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Habit.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


@extend_schema(
    tags=["Student Points"],
    summary="List and award habit points",
    description="Teachers can view their own point logs and create new ones for their students."
)
class StudentPointsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    serializer_class = StudentPointsSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return StudentPoints.objects.filter(
            teacher=self.request.user
        ).select_related("student", "habit")

    def _validate_teacher_ownership(self, *, student, habit):
        user = self.request.user

        if student.teacher_id != user.id: # type: ignore
            raise PermissionDenied("You can only award points to your own students.")

        if habit.teacher_id != user.id: # type: ignore
            raise PermissionDenied("You can only use habits you created.")

    def perform_create(self, serializer):
        student = serializer.validated_data["student"]
        habit = serializer.validated_data["habit"]
        self._validate_teacher_ownership(student=student, habit=habit)
        serializer.save(
            teacher=self.request.user,
            points=habit.points,
        )
