from rest_framework import serializers
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
            "teacher_id"
        ]