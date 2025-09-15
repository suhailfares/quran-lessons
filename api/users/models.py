from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    # Remove username requirement, use email instead
    username = None
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mosque_name = models.CharField(max_length=150, blank=True, null=True)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # no username required

    def __str__(self):
        return f"{self.email} ({self.role})"

    class Meta:
        db_table = 'users'