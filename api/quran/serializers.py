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
    label = serializers.ChoiceField(choices=StudentHifz.Label.choices, required=False)
    date = serializers.DateTimeField()

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        if getattr(user, "role", None) != "teacher":
            raise serializers.ValidationError("Only teachers can create hifz records.")

        try:
            student = Student.objects.select_related("teacher").get(id=data["student_id"])
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Student not found."})

        if student.teacher_id != user.id:
            raise serializers.ValidationError("This student does not belong to the authenticated teacher.")

        try:
            chapter = Chapter.objects.get(index=data["chapter_index"])
        except Chapter.DoesNotExist:
            raise serializers.ValidationError({"chapter_index": "Chapter with this index does not exist."})

        if data["start"] > data["end"]:
            raise serializers.ValidationError({"range": "start must be <= end."})

        if chapter.totalVerses and data["end"] > chapter.totalVerses:
            raise serializers.ValidationError({
                "range": f"end exceeds chapter's total verses ({chapter.totalVerses})."
            })

        data["student_obj"] = student
        data["chapter_obj"] = chapter
        return data

    def create(self, validated_data):
        student = validated_data["student_obj"]
        chapter = validated_data["chapter_obj"]
        notes = validated_data.get("notes")
        created_at = validated_data["date"]

        create_kwargs = dict(
            student=student,
            chapter=chapter,
            start_verse=validated_data["start"],
            end_verse=validated_data["end"],
            notes=notes,
            created_at=created_at,
        )
        if "label" in validated_data:
            create_kwargs["label"] = validated_data["label"]

        try:
            obj = StudentHifz.objects.create(**create_kwargs)
        except IntegrityError:
            raise serializers.ValidationError(
                "An identical range already exists for this student and chapter."
            )

        return obj


class StudentHifzUpdateSerializer(serializers.Serializer):
    chapter_index = serializers.IntegerField(required=False)
    start = serializers.IntegerField(min_value=1, required=False)
    end = serializers.IntegerField(min_value=1, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    label = serializers.ChoiceField(choices=StudentHifz.Label.choices, required=False)
    date = serializers.DateTimeField(required=False)

    def update(self, instance, validated_data):
        if "chapter_index" in validated_data:
            try:
                chapter = Chapter.objects.get(index=validated_data["chapter_index"])
            except Chapter.DoesNotExist:
                raise serializers.ValidationError({"chapter_index": "Chapter with this index does not exist."})
            instance.chapter = chapter

        if "start" in validated_data:
            instance.start_verse = validated_data["start"]
        if "end" in validated_data:
            instance.end_verse = validated_data["end"]
        if "notes" in validated_data:
            instance.notes = validated_data["notes"]
        if "label" in validated_data:
            instance.label = validated_data["label"]
        if "date" in validated_data:
            instance.created_at = validated_data["date"]

        if instance.start_verse > instance.end_verse:
            raise serializers.ValidationError({"range": "start must be <= end."})
        if instance.chapter.totalVerses and instance.end_verse > instance.chapter.totalVerses:
            raise serializers.ValidationError({
                "range": f"end exceeds chapter's total verses ({instance.chapter.totalVerses})."
            })

        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError(
                "An identical range already exists for this student and chapter."
            )
        return instance


class StudentHifzSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    chapter_index = serializers.IntegerField(source="chapter.index")
    start = serializers.IntegerField(source="start_verse")
    end = serializers.IntegerField(source="end_verse")
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    label = serializers.CharField()
    date = serializers.DateTimeField(source="created_at")
    updated_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
