from django.contrib import admin

from students.models import Student


# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "father_name",
        "mother_name",
        "school",
        "teacher",
        "created_at",
    )
    list_filter = ("school", "teacher", "created_at")
    search_fields = (
        "first_name",
        "last_name",
        "father_name",
        "mother_name",
        "school",
        "teacher__username",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)