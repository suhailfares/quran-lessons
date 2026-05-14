from rest_framework import serializers

from habits.models import Habit, StudentPoints


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            "id", "name", "description", "points", "minusPoints", "teacher",
            "updated_at", "is_deleted",
        ]
        read_only_fields = ["teacher", "updated_at", "is_deleted"]


class StudentPointsSerializer(serializers.ModelSerializer):
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
        read_only_fields = ["id", "teacher", "created_at", "updated_at", "is_deleted"]
