from django.db import models
from django.utils import timezone

from students.models import Student

# Create your models here.

class Part(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    arTitle = models.CharField(max_length=100, blank=True)
    index = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    arTitle = models.CharField(max_length=100, blank=True)
    index = models.PositiveIntegerField(unique=True)
    parts = models.ManyToManyField(
        Part,
        related_name="chapters",
        blank=False
    )
    totalVerses = models.PositiveIntegerField(default=0)

class Verse(models.Model):
    id = models.AutoField(primary_key=True)
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.PROTECT,
        related_name="verses",
    )

    part = models.ForeignKey(
        Part,
        on_delete=models.PROTECT,
        related_name="verses",
        null=True,
        blank=True
    )

    index = models.PositiveIntegerField()
    text = models.TextField(blank=True)

    class Meta:
        unique_together= ("chapter", "index")
        ordering = ["chapter_id", "index"]

    def __str__(self):
        return f"{self.chapter.title} - {self.index}"

class StudentHifz(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="hifz_entries"
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.PROTECT,
        related_name="hifz_entries",
    )
    start_verse = models.PositiveIntegerField(default=1)
    end_verse = models.PositiveIntegerField(default=1)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    ## TODO: CREATE CUSTOM DATE
    ## TODO: CREATE MODE (Repetition, Memorization, Improvement)

    class Meta:
        db_table = "student_hifz"
        indexes = [
            models.Index(fields=["student", "chapter"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["student", "chapter", "start_verse", "end_verse"],
                name="Exact chapter and verses range per student"
            )
        ]

    def __str__(self):
        return f"{self.student} | {self.chapter.title} {self.start_verse}-{self.end_verse}"
