from django.db import models

class Item(models.Model):
    # id field is created automatically by Django as primary key
    name = models.CharField(max_length=200)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sensors')
    plant_name = models.CharField(max_length=100)
    pump_thr = models.FloatField(default=50)
    humidity = models.FloatField(default=0)
    temp = models.FloatField(default=0)
    light = models.FloatField(default=0)

    def __str__(self):
        return f"{self.plant_name} sensor at {self.item.name}"
