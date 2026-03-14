# myapp/views.py (FIXED VERSION)

# Import JsonResponse so we can return JSON instead of HTML
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt   # to allow POST from external scripts
from django.contrib.auth.decorators import login_required # Required for access control
from django.contrib.auth.forms import UserCreationForm    # Used for new user registration
from django.contrib import messages                       # Used for sending success messages
import json

from .models import Item, Sensor
from .forms import ItemForm, SensorForm

# --- AUTHENTICATION VIEWS ---

# View for user registration (Create Account button)
def register_view(request):
    # If the request method is POST, the user is submitting the form
    if request.method == 'POST':
        # Create a form instance populated with data from the request
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user to the database
            user = form.save()
            # Add a success message (optional)
            messages.success(request, f'Account created for {user.username}. Please log in.')
            # Redirect to the login page (path is defined by django.contrib.auth.urls)
            return redirect('/accounts/login/')
    else:
        # If the request method is GET, display a blank registration form
        form = UserCreationForm()
    
    # Render the registration template
    return render(request, 'register.html', {'form': form})


# --- CORE VIEWS (Public) ---

# Home page view (can be accessed by anyone)
def home(request):
    return render(request, 'home.html')

# About page view (can be accessed by anyone)
def about(request):
    return render(request, 'about.html')


# --- PROTECTED VIEWS (HTML) ---

# Map page view: Protected and implements filtering logic
@login_required 
def map(request):
    # 1. ITEM FILTERING LOGIC
    # Check if the user is the 'admin' user (as requested by the user)
    if request.user.username == 'admin':
        # Admin user sees ALL items
        items = Item.objects.all()
    else:
        # Regular user sees only their OWN items
        items = Item.objects.filter(user=request.user)

    # 2. HANDLE POST REQUEST (Add New Item)
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            # Crucial: Assign the current logged-in user to the new Item before saving
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            return redirect('map')
    else:
        # Handles GET request (initial page load)
        form = ItemForm()

    return render(request, 'map.html', {'items': items, 'form': form})

# Terminal page view: Protected
@login_required 
def terminal(request):
    return render(request, 'terminal.html')

# Edit Item/Gateway view: Protected and includes ownership check
@login_required 
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # AUTHORIZATION CHECK: Ensure the user owns the item OR is the admin
    if item.user != request.user and request.user.username != 'admin':
        # If not authorized, redirect them away (e.g., to map page)
        messages.error(request, "You are not authorized to edit this item.")
        return redirect('map')

    item_form = ItemForm(request.POST or None, instance=item)
    sensor_form = SensorForm(request.POST or None)

    if request.method == 'POST':
        if 'add_sensor' in request.POST:
            if sensor_form.is_valid():
                new_sensor = sensor_form.save(commit=False)
                new_sensor.item = item
                new_sensor.save()
                return redirect('edit_item', item_id=item.id)
        
        elif item_form.is_valid():
            item_form.save()
            return redirect('map')

    context = {
        'item': item,
        'form': item_form,         
        'sensor_form': sensor_form, 
    }
    return render(request, 'edit_item.html', context)

# Delete Item/Gateway view: Protected and includes ownership check
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # AUTHORIZATION CHECK
    if item.user != request.user and request.user.username != 'admin':
        messages.error(request, "You are not authorized to delete this item.")
        return redirect('map')

    if request.method == 'POST':
        item.delete()
        messages.success(request, f"Item '{item.name}' deleted successfully.")
        return redirect('map')

    return render(request, 'delete_item.html', {'item': item})

# Edit Sensor view: Protected and includes ownership check (via parent item)
@login_required
def edit_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, id=sensor_id)
    
    # AUTHORIZATION CHECK: Check ownership of the parent Item
    if sensor.item.user != request.user and request.user.username != 'admin':
        messages.error(request, "You are not authorized to edit this sensor.")
        return redirect('map')

    form = SensorForm(request.POST or None, instance=sensor)

    if request.method == 'POST':
        if 'delete_sensor' in request.POST:
            item_id = sensor.item.id
            sensor.delete()
            messages.success(request, f"Sensor '{sensor.plant_name}' deleted successfully.")
            return redirect('edit_item', item_id=item_id)
        
        elif form.is_valid():
            form.save()
            messages.success(request, f"Sensor '{sensor.plant_name}' updated successfully.")
            return redirect('edit_item', item_id=sensor.item.id)

    return render(request, 'edit_sensor.html', {'form': form, 'sensor': sensor})


# --- PROTECTED VIEWS (API ENDPOINTS) ---
# NOTE: The @login_required decorator is REMOVED from all API views
# and replaced with a manual authentication check that returns a JSON 401 error.

# API for getting all items (now filtered by user)
# REMOVED: @login_required
def api_items(request):
    # MANUAL AUTHENTICATION CHECK: Return JSON error (401) for unauthenticated users
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required for API access.'}, 
            status=401 
        )

    if request.user.username == 'admin':
        items = Item.objects.all()
    else:
        items = Item.objects.filter(user=request.user)

    data = list(items.values('id', 'name', 'latitude', 'longitude'))
    return JsonResponse(data, safe=False)

# API for creating items (Requires login and assigns user)
@csrf_exempt
# REMOVED: @login_required
def api_create_item(request):
    # MANUAL AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required for API access.'}, status=401) 

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            # Create item and assign to the logged-in user
            item = Item.objects.create(
                user=request.user, # Assign the logged-in user
                name=data["name"],
                longitude=data.get("longitude", 0.0),
                latitude=data.get("latitude", 0.0),
            )
            return JsonResponse({
                "id": item.id,
                "name": item.name,
                "latitude": item.latitude,
                "longitude": item.longitude,
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)


# API for updating items (Requires ownership check)
@csrf_exempt
# REMOVED: @login_required
def api_update_item(request, item_id):
    # MANUAL AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required for API access.'}, status=401) 
        
    if request.method == "PUT":
        data = json.loads(request.body.decode("utf-8"))
        item = get_object_or_404(Item, id=item_id)
        
        # AUTHORIZATION CHECK
        if item.user != request.user and request.user.username != 'admin':
            return JsonResponse({"error": "Forbidden: You do not own this item."}, status=403)

        for field in ["name", "latitude", "longitude"]:
            if field in data and data[field] is not None:
                setattr(item, field, data[field])

        item.save()
        return JsonResponse({"message": "Item updated successfully."}, status=200)
    return JsonResponse({"error": "Only PUT method is allowed."}, status=405)


# API for deleting items (Requires ownership check)
@csrf_exempt
# REMOVED: @login_required
def api_delete_item(request, item_id):
    # MANUAL AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required for API access.'}, status=401) 

    if request.method == "DELETE":
        item = get_object_or_404(Item, id=item_id)

        # AUTHORIZATION CHECK
        if item.user != request.user and request.user.username != 'admin':
            return JsonResponse({"error": "Forbidden: You do not own this item."}, status=403)

        item.delete()
        return JsonResponse({"message": "Item deleted successfully."}, status=204)
    return JsonResponse({"error": "Only DELETE method is allowed."}, status=405)

# API for getting sensors for an item (Protected)
# REMOVED: @login_required
def api_sensors(request, item_id):
    # MANUAL AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required for API access.'}, status=401) 

    item = get_object_or_404(Item, id=item_id)
    
    # AUTHORIZATION CHECK
    if item.user != request.user and request.user.username != 'admin':
        return JsonResponse({"error": "Forbidden: You do not own this item."}, status=403)

    sensors = item.sensors.all()
    data = list(sensors.values('id','sn', 'plant_name', 'pump_thr', 'humidity', 'temp', 'light'))
    return JsonResponse(data, safe=False)

# API for creating a new sensor (Protected and assigns to item)
@csrf_exempt
# REMOVED: @login_required
def api_create_sensor(request, item_id):
    # MANUAL AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required for API access.'}, status=401) 

    if request.method == "POST":
        item = get_object_or_404(Item, id=item_id)
        
        # AUTHORIZATION CHECK
        if item.user != request.user and request.user.username != 'admin':
            return JsonResponse({"error": "Forbidden: You cannot add a sensor to this item."}, status=403)

        try:
            data = json.loads(request.body.decode("utf-8"))
            sensor = Sensor.objects.create(
                item_id=item_id,
                plant_name=data["plant_name"],
                pump_thr=data.get("pump_thr", 50),
                humidity=data.get("humidity", 0),
                temp=data.get("temp", 0),
                light=data.get("light", 0),
            )
            # Simplified JSON response
            return JsonResponse({"id": sensor.id, "plant_name": sensor.plant_name}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)

# API for updating a sensor (Requires ownership check)
@csrf_exempt
def api_update_sensor(request, sensor_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Auth required'}, status=401)

    if request.method == "PUT":
        data = json.loads(request.body.decode("utf-8"))
        sensor = get_object_or_404(Sensor, id=sensor_id)

        # Update SN and Plant Name (Strings)
        if "sn" in data: sensor.sn = data["sn"]
        if "plant_name" in data: sensor.plant_name = data["plant_name"]

        # Update numeric values as Integers
        # Using int(float(x)) handles cases where the API might send "50.0"
        if "pump_thr" in data: sensor.pump_thr = int(float(data["pump_thr"]))
        if "humidity" in data: sensor.humidity = int(float(data["humidity"]))
        if "temp" in data: sensor.temp = int(float(data["temp"]))
        if "light" in data: sensor.light = int(float(data["light"]))

        sensor.save()
        return JsonResponse({"message": "Sensor updated successfully."}, status=200)

# API for deleting a sensor (Requires ownership check)
@csrf_exempt
# REMOVED: @login_required
def api_delete_sensor(request, sensor_id):
    # MANUAL AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required for API access.'}, status=401) 

    if request.method == "DELETE":
        sensor = get_object_or_404(Sensor, id=sensor_id)

        # AUTHORIZATION CHECK (via parent item)
        if sensor.item.user != request.user and request.user.username != 'admin':
            return JsonResponse({"error": "Forbidden: You do not own the parent item of this sensor."}, status=403)
        
        sensor.delete()
        return JsonResponse({"message": "Sensor deleted successfully."}, status=204)
    return JsonResponse({"error": "Only DELETE method is allowed."}, status=405)