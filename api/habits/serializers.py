from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "name", "description", "points", "teacher"]
        read_only_fields = ["teacher"]

class StudentPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPoints
        fields = [
            "id",
            "student",
            "habit",
            "teacher",
            "points",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]