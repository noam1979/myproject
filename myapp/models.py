# models.py
from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    longitude = models.FloatField(default=0.0) # Keep as float for GPS
    latitude = models.FloatField(default=0.0)  # Keep as float for GPS

    def __str__(self):
        return f"{self.name} by {self.user.username}"

class Sensor(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sensors')
    sn = models.CharField(max_length=50, default="0", verbose_name="SN")
    plant_name = models.CharField(max_length=100)
    
    # Changed these to IntegerField
    pump_thr = models.IntegerField(default=50)
    humidity = models.IntegerField(default=0)
    temp = models.IntegerField(default=0)
    light = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.sn}] {self.plant_name}"