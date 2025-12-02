from django.db import models
from django.contrib.auth.models import User # Import the built-in User model

# --- Item Model (Gateway) ---
class Item(models.Model):
    
    #    Foreign Key linking the Item to the User who created it.
    #    When the User is deleted, their Items are deleted too (CASCADE).
    user = models.ForeignKey(User, on_delete=models.CASCADE)

# id field is created automatically by Django as primary key
    name = models.CharField(max_length=200)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    def __str__(self):
        # Improved string representation to show the Item and its owner
        return f"{self.name} by {self.user.username}"

# --- Sensor Model ---
class Sensor(models.Model):
    # Foreign Key linking the sensor to its parent Item (Gateway)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sensors')
    plant_name = models.CharField(max_length=100)
    pump_thr = models.FloatField(default=50)
    humidity = models.FloatField(default=0)
    temp = models.FloatField(default=0)
    light = models.FloatField(default=0)

    def __str__(self):
        return f"{self.plant_name} sensor at {self.item.name}"
