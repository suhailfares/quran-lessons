from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number", "mosque_name", "role")}),
    ) # type: ignore
    list_display = ("username", "email", "first_name", "last_name", "role")