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