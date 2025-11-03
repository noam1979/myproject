# Import JsonResponse so we can return JSON instead of HTML
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from .forms import ItemForm

# Import JsonResponse and Json parser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt   # to allow POST from external scripts
import json



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

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('map')
    else:
        form = ItemForm(instance=item)

    return render(request, 'edit_item.html', {'form': form, 'item': item})

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