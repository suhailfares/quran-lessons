from django.db import IntegrityError
from rest_framework import serializers

from quran.models import Chapter, StudentHifz
from students.models import Student


class StudentHifzCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    chapter_index = serializers.IntegerField()
    start = serializers.IntegerField(min_value=1)
    end = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date = serializers.DateTimeField()

    mode = serializers.ChoiceField(
        choices=StudentHifz.Mode.choices,
        default=StudentHifz.Mode.MEMORIZATION,
        required=True
    )

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        # must be a teacher
        if getattr(user, "role", None) != "teacher":
            raise serializers.ValidationError("Only teachers can create hifz records.")

        # student must exist and belong to this teacher
        try:
            student = Student.objects.select_related("teacher").get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Student not found."})

        if student.teacher_id != user.id:
            raise serializers.ValidationError("This student does not belong to the authenticated teacher.")

        # chapter by index
        try:
            chapter = Chapter.objects.get(index=data["chapter_index"])
        except Chapter.DoesNotExist:
            raise serializers.ValidationError({"chapter_index": "Chapter with this index does not exist."})

        # range rules
        if data["start"] > data["end"]:
            raise serializers.ValidationError({"range": "start must be <= end."})

        if chapter.totalVerses and data["end"] > chapter.totalVerses:
            raise serializers.ValidationError({
                "range": f"end exceeds chapter's total verses ({chapter.totalVerses})."
            })

        # stash resolved objects
        data["student_obj"] = student
        data["chapter_obj"] = chapter
        return data

    def create(self, validated_data):
        student = validated_data["student_obj"]
        chapter = validated_data["chapter_obj"]
        notes = validated_data.get("notes")
        created_at = validated_data["date"]
        mode = validated_data["mode", StudentHifz.Mode.MEMORIZATION]

        try:
            obj = StudentHifz.objects.create(
                student=student,
                chapter=chapter,
                start_verse=validated_data["start"],
                end_verse=validated_data["end"],
                notes=notes,
                created_at=created_at,
                mode=mode
            )
        except IntegrityError:
            raise serializers.ValidationError(
                "An identical range already exists for this student and chapter."
            )

        return obj


class StudentHifzSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    chapter_index = serializers.IntegerField()
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    date = serializers.DateTimeField(source="created_at")
    mode = serializers.ChoiceField(choices=StudentHifz.Mode.choices)
