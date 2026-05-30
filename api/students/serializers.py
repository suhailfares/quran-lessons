from rest_framework import serializers

from quranlessons.serializers import TeacherAssignableSerializerMixin
from .models import Student


class StudentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "first_name", "last_name", "father_name", "mother_name",
            "date_of_birth", "phone_number", "parent_phone_number",
            "birth_place", "school"
        ]


class StudentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id", "first_name", "last_name", "father_name", "mother_name",
            "date_of_birth", "phone_number", "parent_phone_number",
            "birth_place", "school", "created_at",
            "teacher_id", "updated_at", "is_deleted",
        ]


class StudentSerializer(TeacherAssignableSerializerMixin):
    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "father_name",
            "mother_name",
            "date_of_birth",
            "phone_number",
            "parent_phone_number",
            "birth_place",
            "school",
            "teacher",
            "teacher_id",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = ["id", "teacher_id", "created_at", "updated_at", "is_deleted"]
