from django.db import models

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

    def __str__(self):
        return self.name