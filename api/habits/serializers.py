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
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = ["id", "teacher", "points", "created_at", "updated_at", "is_deleted"]


class StudentPointsBatchEntrySerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    habit_id = serializers.IntegerField()
    plus_count = serializers.IntegerField(min_value=0)
    minus_count = serializers.IntegerField(min_value=0)


class StudentPointsBatchPayloadSerializer(serializers.Serializer):
    date = serializers.DateField()
    lesson_id = serializers.IntegerField(required=False, allow_null=True)
    entries = StudentPointsBatchEntrySerializer(many=True)


class StudentPointsBatchResponseSerializer(serializers.Serializer):
    written = serializers.IntegerField()
    deleted = serializers.IntegerField()
