from django import forms
from .models import Item
from .models import Sensor

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'longitude', 'latitude']

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['sn','plant_name', 'pump_thr', 'humidity', 'temp', 'light']
