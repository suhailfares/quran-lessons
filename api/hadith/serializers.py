from rest_framework import serializers

from hadith.models import HadithSabr, HadithHifz
from quranlessons.roles import is_strict_admin, is_manager
from students.models import Student


class HadithSabrCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    hadith_type = serializers.ChoiceField(choices=HadithSabr.Type.choices)

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        if not (getattr(user, "role", None) == "teacher" or is_strict_admin(user) or is_manager(user)):
            raise serializers.ValidationError("Only teachers can create hadith sabr records.")

        try:
            student = Student.objects.select_related("teacher").get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Student not found."})

        if is_strict_admin(user):
            pass
        elif is_manager(user):
            if student.teacher.mosque_name != user.mosque_name:
                raise serializers.ValidationError("This student does not belong to your mosque.")
        elif student.teacher_id != user.id:
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


class HadithHifzCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    hadith_numbers = serializers.ListField(child=serializers.IntegerField(min_value=1))
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    label = serializers.ChoiceField(choices=HadithHifz.Label.choices, required=False)
    date = serializers.DateTimeField()

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        if not (getattr(user, "role", None) == "teacher" or is_strict_admin(user) or is_manager(user)):
            raise serializers.ValidationError("Only teachers can create hadith hifz records.")

        try:
            student = Student.objects.select_related("teacher").get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Student not found."})

        if is_strict_admin(user):
            pass
        elif is_manager(user):
            if student.teacher.mosque_name != user.mosque_name:
                raise serializers.ValidationError("This student does not belong to your mosque.")
        elif student.teacher_id != user.id:
            raise serializers.ValidationError("This student does not belong to the authenticated teacher.")

        if not data["hadith_numbers"]:
            raise serializers.ValidationError({"hadith_numbers": "At least one hadith number is required."})

        data["student_obj"] = student
        return data

    def create(self, validated_data):
        student = validated_data["student_obj"]
        notes = validated_data.get("notes")
        created_at = validated_data["date"]

        create_kwargs = dict(
            student=student,
            hadith_numbers=validated_data["hadith_numbers"],
            notes=notes,
            created_at=created_at,
        )
        if "label" in validated_data:
            create_kwargs["label"] = validated_data["label"]

        obj = HadithHifz.objects.create(**create_kwargs)
        return obj


class HadithHifzUpdateSerializer(serializers.Serializer):
    hadith_numbers = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    label = serializers.ChoiceField(choices=HadithHifz.Label.choices, required=False)
    date = serializers.DateTimeField(required=False)

    def update(self, instance, validated_data):
        if "hadith_numbers" in validated_data:
            if not validated_data["hadith_numbers"]:
                raise serializers.ValidationError({"hadith_numbers": "At least one hadith number is required."})
            instance.hadith_numbers = validated_data["hadith_numbers"]
        if "notes" in validated_data:
            instance.notes = validated_data["notes"]
        if "label" in validated_data:
            instance.label = validated_data["label"]
        if "date" in validated_data:
            instance.created_at = validated_data["date"]

        instance.save()
        return instance


class HadithHifzSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    hadith_numbers = serializers.ListField(child=serializers.IntegerField())
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    label = serializers.CharField()
    date = serializers.DateTimeField(source="created_at")
    updated_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
