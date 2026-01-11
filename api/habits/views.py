from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from habits.models import Habit
from habits.permissions import IsTeacher
from habits.serializers import HabitSerializer


# Create your views here.

@extend_schema(
    tags=["Habits"],
    summary="Manage Habits for current teacher",
    description="habits"
)
class HabitViewSet(ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Habit.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class StudentPointsViewSet(ModelViewSet):
    serializer_class = StudentPointsSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        """
        Teachers can only see point records they created.
        """
        return StudentPoints.objects.filter(
            teacher=self.request.user
        ).select_related("student", "habit")

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in teacher.
        """
        serializer.save(teacher=self.request.user)

    def perform_update(self, serializer):
        """
        Prevent changing ownership.
        """
        if serializer.instance.teacher != self.request.user:
            raise PermissionDenied("You cannot modify this record.")

        serializer.save()

    def perform_destroy(self, instance):
        """
        Prevent deleting others' records.
        """
        if instance.teacher != self.request.user:
            raise PermissionDenied("You cannot delete this record.")

        instance.delete()