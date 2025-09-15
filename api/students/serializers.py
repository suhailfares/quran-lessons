from rest_framework import serializers
from .models import Student
from users.models import User

class StudentSerializer(serializers.ModelSerializer):
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="teacher"),
        source="teacher",
        write_only=True
    )
    teacher = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id", "first_name", "last_name", "father_name", "mother_name",
            "date_of_birth", "phone_number", "parent_phone_number",
            "birth_place", "school", "created_at",
            "teacher", "teacher_id"
        ]

