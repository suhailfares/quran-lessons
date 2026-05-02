from django.contrib.auth.models import AbstractUser
from django.db import models

from institutes.models import Institute


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mosque_name = models.CharField(max_length=150, blank=True, null=True)

    institute = models.ForeignKey(
        Institute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('institute_admin', 'Institute Admin'),
        ('institute_user', 'Institute User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


    class Meta:
        db_table = 'users'