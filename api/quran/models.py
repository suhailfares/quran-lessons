from django.db import models

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
    )

    index = models.PositiveIntegerField()
    text = models.TextField(blank=True)

    class Meta:
        unique_together= ("chapter", "index")
        ordering = ["chapter_id", "index"]

    def __str__(self):
        return f"{self.chapter.title} - {self.index}"