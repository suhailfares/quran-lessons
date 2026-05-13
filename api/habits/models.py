from django.db import models
from django.utils import timezone

from students.models import Student
from users.models import User


# Create your models here.

class Habit(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    points = models.IntegerField(default=1)
    minusPoints = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class StudentPoints(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="point_records"
    )

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    lesson = models.ForeignKey(
        "lessons.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_points",
    )

    isMinus = models.BooleanField(default=False)

    points = models.IntegerField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.habit.name}"
