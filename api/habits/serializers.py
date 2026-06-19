from rest_framework import serializers

from habits.models import Habit, StudentPoints
from quranlessons.serializers import TeacherAssignableSerializerMixin


class HabitSerializer(TeacherAssignableSerializerMixin):
    class Meta:
        model = Habit
        fields = [
            "id", "name", "description", "points", "minusPoints", "allowNegative", "oncePerDay", "teacher",
            "updated_at", "is_deleted",
        ]
        read_only_fields = ["updated_at", "is_deleted"]


class StudentPointsSerializer(TeacherAssignableSerializerMixin):
    class Meta:
        model = StudentPoints
        fields = [
            "id",
            "student",
            "habit",
            "teacher",
            "lesson",
            "isMinus",
            "points",
            "date",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_deleted"]
