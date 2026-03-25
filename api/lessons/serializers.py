from rest_framework import serializers
from lessons.models import Lesson, Attendance
from students.serializers import StudentSerializer


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
            "attended"
        ]
        read_only_fields = ["id"]


class StudentEntrySerializer(serializers.Serializer):
    studentId = serializers.IntegerField()


class BulkAttendancePayloadSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField(required=False)
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

        if not attrs["students"]:
            raise serializers.ValidationError({"students": "Provide at least one entry."})
        return attrs


class AttendanceListResponseSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    students = StudentSerializer(many=True)
