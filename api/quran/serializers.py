from rest_framework import serializers

from quran.models import Chapter, StudentHifz, UserHifz, QuranSabr, Verse
from quranlessons.roles import is_strict_admin, is_manager
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

        if not (getattr(user, "role", None) == "teacher" or is_strict_admin(user) or is_manager(user)):
            raise serializers.ValidationError("Only teachers can create hifz records.")

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

        obj = StudentHifz.objects.create(**create_kwargs)
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

        instance.save()
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


class QuranSabrCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    sabr_type = serializers.ChoiceField(choices=QuranSabr.Type.choices)
    range = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=30),
        min_length=2,
        max_length=2
    )

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        if not (getattr(user, "role", None) == "teacher" or is_strict_admin(user) or is_manager(user)):
            raise serializers.ValidationError("Only teachers can create quran sabr records.")

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

        range_vals = data["range"]
        if range_vals[0] > range_vals[1]:
            raise serializers.ValidationError({"range": "First value must be <= second value."})

        data["student_obj"] = student
        data["range_start"] = range_vals[0]
        data["range_end"] = range_vals[1]
        return data

    def create(self, validated_data):
        obj = QuranSabr.objects.create(
            student=validated_data["student_obj"],
            sabr_type=validated_data["sabr_type"],
            range_start=validated_data["range_start"],
            range_end=validated_data["range_end"],
        )
        return obj


class QuranSabrSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    sabr_type = serializers.CharField()
    range = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)

    def get_range(self, obj):
        return [obj.range_start, obj.range_end]


class UserHifzJuzRangeCreateSerializer(serializers.Serializer):
    juz_range = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=30),
        min_length=2,
        max_length=2,
    )
    label = serializers.ChoiceField(choices=UserHifz.Label.choices, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date = serializers.DateTimeField(required=False)

    def validate_juz_range(self, value):
        if value[0] > value[1]:
            raise serializers.ValidationError("First juz must be <= second juz.")
        return value

    def create(self, validated_data):
        from django.utils import timezone
        user = self.context["request"].user
        juz_start, juz_end = validated_data["juz_range"]
        label = validated_data.get("label", UserHifz.Label.MEMORIZATION)
        notes = validated_data.get("notes")
        date = validated_data.get("date", timezone.now())

        verses = (
            Verse.objects
            .filter(part__index__range=(juz_start, juz_end))
            .select_related("chapter")
            .order_by("chapter__index", "index")
        )

        chapter_ranges = {}
        for verse in verses:
            c_idx = verse.chapter.index
            v_idx = verse.index
            if c_idx not in chapter_ranges:
                chapter_ranges[c_idx] = {"chapter": verse.chapter, "min": v_idx, "max": v_idx}
            else:
                if v_idx < chapter_ranges[c_idx]["min"]:
                    chapter_ranges[c_idx]["min"] = v_idx
                if v_idx > chapter_ranges[c_idx]["max"]:
                    chapter_ranges[c_idx]["max"] = v_idx

        entries = [
            UserHifz(
                user=user,
                chapter=data["chapter"],
                start_verse=data["min"],
                end_verse=data["max"],
                label=label,
                notes=notes,
                created_at=date,
            )
            for _, data in sorted(chapter_ranges.items())
        ]
        UserHifz.objects.bulk_create(entries)
        return entries


class UserHifzSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    chapter_index = serializers.IntegerField(source="chapter.index")
    start = serializers.IntegerField(source="start_verse")
    end = serializers.IntegerField(source="end_verse")
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    label = serializers.CharField()
    date = serializers.DateTimeField(source="created_at")
    updated_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)


