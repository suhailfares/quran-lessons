from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Lesson, Attendance


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "teacher")
    ordering = ("id",)
    search_fields = ("subject", "teacher__first_name", "teacher__last_name", "teacher__email")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "lesson", "attended")
    ordering = ("lesson", "student")
    list_filter = ("lesson", "attended")
    search_fields = ("student__first_name", "student__last_name", "lesson__subject")
