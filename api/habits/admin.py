from django.contrib import admin

from habits.models import Habit, StudentPoints


# Register your models here.

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "teacher", "points")
    list_filter = ("teacher",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(StudentPoints)
class StudentPointsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "habit",
        "teacher",
        "points",
        "created_at",
    )

    list_filter = ("teacher", "habit", "created_at")
    search_fields = (
        "student__name",
        "habit__name",
        "teacher__username",
    )

    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
