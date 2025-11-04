from rest_framework import serializers
from lessons.models import Lesson, Attendance


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "subject",
            "teacher"
        ]
        read_only_fields = ["id", "teacher"]
        
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "id",
            "student",
            "lesson",
            "attended"
        ]
        read_only_fields = ["id"]
