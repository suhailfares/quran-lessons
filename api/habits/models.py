from django.db import models

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

    isMinus = models.BooleanField(default=False)

    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.habit.name}"
