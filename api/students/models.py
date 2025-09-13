from django.db import models
from django.conf import settings
# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    parent_phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_place = models.CharField(max_length=100, blank=True, null=True) 
    school = models.CharField(max_length=150)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'teacher'}, 
        related_name='students'
    ) 

    created_at = models.DateTimeField(auto_now_add=True)  # auto timestamp

    def __str__(self):
        return f"{self.first_name} {self.last_name}"