from django.db import models

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

    class Meta:
        unique_together = ('student', 'lesson') # no same student in the same lesson

    def __str__(self):
        return f"{self.student} - {self.lesson} - {'Present' if self.attended else 'Absent'}"
