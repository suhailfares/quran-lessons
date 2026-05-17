from django.db import models
from django.utils import timezone

from students.models import Student


class HadithSabr(models.Model):
    class Type(models.TextChoices):
        NAWAWI = "الأربعين النووية", "الأربعين النووية"

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="hadith_sabr_entries"
    )
    hadith_type = models.CharField(
        max_length=50,
        choices=Type.choices,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "hadith_sabr"

    def __str__(self):
        return f"{self.student} | {self.hadith_type}"
