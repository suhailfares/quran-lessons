from django.db import models
from django.utils import timezone

from students.models import Student
from users.models import User


# Create your models here.

class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    """ TODO: later turn this into its own subjects table -> Quran, Tajweed, 3aqidah, 7adith.... """
    subject = models.CharField(max_length=100)

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} by {self.teacher}"


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    attended = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "student", "date"],
                name="unique_attendance_lesson_student_date",
            ),
        ]

    def __str__(self):
        return f"{self.student} - {self.lesson} - {'Present' if self.attended else 'Absent'}"
