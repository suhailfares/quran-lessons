from django.db import models

# Create your models here.

class Part(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    parts = models.ManyToManyField(
        Part,
        related_name="chapters",
        blank=False
    )

class Verse(models.Model):
    id = models.AutoField(primary_key=True)
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.PROTECT,
        related_name="verses",
    )

    number = models.PositiveIntegerField()
    text = models.TextField

    class Meta:
        unique_together= ("chapter", "number")
        ordering = ["chapter_id", "number"]

    def __str__(self):
        return f"{self.chapter.name} - {self.number}"