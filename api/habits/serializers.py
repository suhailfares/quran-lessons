from rest_framework import serializers

from habits.models import Habit, StudentPoints


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "name", "description", "points", "minusPoints", "teacher"]
        read_only_fields = ["teacher"]

class StudentPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPoints
        fields = [
            "id",
            "student",
            "habit",
            "teacher",
            "isMinus",
            "points",
            "created_at",
        ]
        read_only_fields = ["id", "teacher", "points", "created_at"]
