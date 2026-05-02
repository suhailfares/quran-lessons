from django.db import models

# Create your models here.

class Institute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


    def __str__(self):
        return self.name