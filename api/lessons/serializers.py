from rest_framework import serializers
from lessons.models import Lesson, Attendance
from students.serializers import StudentSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "subject",
            "teacher",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = ["id", "teacher", "updated_at", "is_deleted"]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "id",
            "student",
            "attended",
            "date",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = ["id", "updated_at", "is_deleted"]


class StudentEntrySerializer(serializers.Serializer):
    studentId = serializers.IntegerField()


class BulkAttendancePayloadSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField(required=False)
    date = serializers.DateField()
    students = StudentEntrySerializer(many=True)

    def validate(self, attrs):
        path_lesson_id = self.context.get("lesson_id")
        payload_lesson_id = attrs.get("lesson_id")

        if payload_lesson_id is None and path_lesson_id is None:
            raise serializers.ValidationError(
                {"lesson_id": "Provide lesson_id either in the payload or URL."}
            )

        if path_lesson_id is not None and payload_lesson_id is not None and path_lesson_id != payload_lesson_id:
            raise serializers.ValidationError(
                {"lesson_id": "Payload lesson_id does not match URL."}
            )

        attrs["lesson_id"] = payload_lesson_id or path_lesson_id

        if attrs["students"] is None:
            raise serializers.ValidationError({"students": "Provide a students array (may be empty)."})
        return attrs


class AttendanceListResponseSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    date = serializers.DateField()
    students = StudentSerializer(many=True)
