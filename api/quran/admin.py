from django.contrib import admin

from quran.models import Part, Chapter, Verse, StudentHifz


# Register your models here.

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "arTitle", "index")
    ordering = ("index",)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "arTitle", "index", "totalVerses")
    ordering = ("index",)
    filter_horizontal = ("parts",)

@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ("id", "chapter", "part", "index")
    ordering = ("chapter", "index")
    list_filter = ("chapter", "part")
    search_fields = ("chapter__title", "text")

@admin.register(StudentHifz)
class StudentHifzAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "chapter", "notes", "start_verse", "end_verse", "created_at")
    ordering = ("id", "student", "created_at")
    search_fields = ("chapter__title", "text")