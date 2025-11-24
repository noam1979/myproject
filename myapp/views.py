# Import JsonResponse so we can return JSON instead of HTML
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from .forms import ItemForm, SensorForm

# Import JsonResponse and Json parser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt   # to allow POST from external scripts
import json

from .models import Sensor

# Home page view
def home(request):
    # Render the home.html template
    return render(request, 'home.html')

def map(request):
    items = Item.objects.all()

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('map')
    else:
        form = ItemForm()

    return render(request, 'map.html', {'items': items, 'form': form})

def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item_form = ItemForm(instance=item)
    sensor_form = SensorForm()

    if request.method == "POST":
        if 'add_sensor' in request.POST:
            sensor_form = SensorForm(request.POST)
            if sensor_form.is_valid():
                sensor = sensor_form.save(commit=False)
                sensor.item = item
                sensor.save()
        else:
            item_form = ItemForm(request.POST, instance=item)
            if item_form.is_valid():
                item_form.save()
        return redirect('edit_item', item_id=item.id)

    return render(request, 'edit_item.html', {
        'form': item_form,
        'sensor_form': sensor_form,
        'item': item,
    })

def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        item.delete()
        return redirect('map')

    return render(request, 'delete_item.html', {'item': item})

# About view: static page
def about(request):
    return render(request, 'about.html')

from django.shortcuts import render

def terminal(request):
    return render(request, 'terminal.html')

# Import JsonResponse so we can return JSON instead of HTML
from django.http import JsonResponse
# Import the Item model so we can query the database
from .models import Item

# API view that returns all items in JSON format
def api_items(request):
    # Query all items and include only the fields that exist in your model
    items = Item.objects.all().values("id", "name", "latitude", "longitude")
    # Convert QuerySet to list and return as JSON
    return JsonResponse(list(items), safe=False)

@csrf_exempt  # disable CSRF just for this API view
def api_create_item(request):
    """
    API endpoint to create a new Item.
    Accepts POST request with JSON body: {"name": "...", "latitude": ..., "longitude": ...}
    """
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)

            # Create new Item in the database
            item = Item.objects.create(
                name=data["name"],
                latitude=data["latitude"],
                longitude=data["longitude"]
            )

            # Return the created item as JSON
            return JsonResponse(
                {"id": item.id, "name": item.name,
                 "latitude": item.latitude, "longitude": item.longitude},
                status=201
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # If not POST, return error
    return JsonResponse({"error": "POST request required"}, status=405)

@csrf_exempt
def api_update_item(request, item_id):
    """
    API endpoint to update an existing Item.
    Accepts PUT request with JSON body: {"name": "...", "latitude": ..., "longitude": ...}
    """
    if request.method == "PUT":
        try:
            # Parse JSON body
            data = json.loads(request.body)

            # Get the item or return 404 if not found
            item = get_object_or_404(Item, id=item_id)

            # Update fields if provided
            if "name" in data:
                item.name = data["name"]
            if "latitude" in data:
                item.latitude = data["latitude"]
            if "longitude" in data:
                item.longitude = data["longitude"]

            # Save changes
            item.save()

            # Return updated item as JSON
            return JsonResponse(
                {"id": item.id, "name": item.name,
                 "latitude": item.latitude, "longitude": item.longitude},
                status=200
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "PUT request required"}, status=405)

@csrf_exempt
def api_delete_item(request, item_id):
    """
    API endpoint to delete an existing Item.
    Accepts DELETE request at /api/items/<id>/delete/
    """
    if request.method == "DELETE":
        # Get the item or return 404 if not found
        item = get_object_or_404(Item, id=item_id)

        # Delete the item
        item.delete()

        # Return confirmation
        return JsonResponse({"message": f"Item {item_id} deleted"}, status=200)

    return JsonResponse({"error": "DELETE request required"}, status=405)

def edit_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, id=sensor_id)
    form = SensorForm(instance=sensor)

    if request.method == "POST":
        if "delete_sensor" in request.POST:
            sensor.delete()
            # Redirect back to the parent item's edit page
            return redirect("edit_item", item_id=sensor.item.id)
        else:
            form = SensorForm(request.POST, instance=sensor)
            if form.is_valid():
                form.save()
                return redirect("edit_item", item_id=sensor.item.id)

    return render(request, "edit_sensor.html", {
        "form": form,
        "sensor": sensor,
    })

def api_sensors(request, item_id):
    sensors = Sensor.objects.filter(item_id=item_id).values(
        "id", "plant_name", "pump_thr", "humidity", "temp", "light"
    )
    return JsonResponse(list(sensors), safe=False)

@csrf_exempt
def api_create_sensor(request, item_id):
    if request.method == "POST":
        data = json.loads(request.body)
        sensor = Sensor.objects.create(
            item_id=item_id,
            plant_name=data["plant_name"],
            pump_thr=data.get("pump_thr", 50),
            humidity=data.get("humidity", 0),
            temp=data.get("temp", 0),
            light=data.get("light", 0),
        )
        return JsonResponse({
            "id": sensor.id,
            "plant_name": sensor.plant_name,
            "pump_thr": sensor.pump_thr,
            "humidity": sensor.humidity,
            "temp": sensor.temp,
            "light": sensor.light,
        }, status=201)

@csrf_exempt
def api_update_sensor(request, sensor_id):
    if request.method == "PUT":
        data = json.loads(request.body.decode("utf-8"))
        sensor = get_object_or_404(Sensor, id=sensor_id)

        for field in ["plant_name", "pump_thr", "humidity", "temp", "light"]:
            if field in data and data[field] is not None:
                setattr(sensor, field, data[field])

        sensor.save()

        return JsonResponse({
            "id": sensor.id,
            "plant_name": sensor.plant_name,
            "pump_thr": sensor.pump_thr,
            "humidity": sensor.humidity,
            "temp": sensor.temp,
            "light": sensor.light,
        }, status=200)


@csrf_exempt
def api_delete_sensor(request, sensor_id):
    if request.method == "DELETE":
        sensor = get_object_or_404(Sensor, id=sensor_id)
        sensor.delete()
        return JsonResponse({"message": f"Sensor {sensor_id} deleted"})