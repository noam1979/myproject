from django.db import models

class Item(models.Model):
    # id field is created automatically by Django as primary key
    name = models.CharField(max_length=200)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
