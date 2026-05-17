from rest_framework import serializers

from hadith.models import HadithSabr
from students.models import Student


class HadithSabrCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    hadith_type = serializers.ChoiceField(choices=HadithSabr.Type.choices)

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        if getattr(user, "role", None) != "teacher":
            raise serializers.ValidationError("Only teachers can create hadith sabr records.")

        try:
            student = Student.objects.select_related("teacher").get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Student not found."})

        if student.teacher_id != user.id:
            raise serializers.ValidationError("This student does not belong to the authenticated teacher.")

        data["student_obj"] = student
        return data

    def create(self, validated_data):
        obj = HadithSabr.objects.create(
            student=validated_data["student_obj"],
            hadith_type=validated_data["hadith_type"],
        )
        return obj


class HadithSabrSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    hadith_type = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
