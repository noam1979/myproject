import requests  # Used for making HTTP requests to the Django REST API

# ------------------------------------------
# Server URLs
# ------------------------------------------
# You can switch between local and deployed environments by commenting/uncommenting.
# Only one BASE_URL and SENSOR_BASE_URL should be active at a time.

# Deployed server (PythonAnywhere example):
# BASE_URL = "https://noamnadav123.pythonanywhere.com/api/items/"
# SENSOR_BASE_URL = "https://noamnadav123.pythonanywhere.com/api/"

# Local Django server (for development):
BASE_URL = "http://127.0.0.1:8000/api/items/"
SENSOR_BASE_URL = "http://127.0.0.1:8000/api/"

# ------------------------------------------
# SENSOR FUNCTIONS
# ------------------------------------------

def get_sensors(item_id):
    """
    Fetch and print all sensors belonging to a given item.
    """
    url = f"{SENSOR_BASE_URL}items/{item_id}/sensors/"
    r = requests.get(url)
    if r.status_code == 200:
        try:
            sensors = r.json()
            print(f"Sensors for item {item_id}:")
            for s in sensors:
                print(f"- {s['id']}: {s['plant_name']} "
                      f"(PumpThr: {s['pump_thr']}, Hum: {s['humidity']}, "
                      f"Temp: {s['temp']}, Light: {s['light']})")
        except ValueError:
            print("Error parsing sensors:", r.text)
    else:
        print("Error:", r.status_code, r.text)


def create_sensor(item_id, plant_name, pump_thr=50, humidity=0, temp=0, light=0):
    """
    Create a new sensor for a specific item.
    Optional parameters: pump_thr, humidity, temp, light.
    """
    url = f"{SENSOR_BASE_URL}items/{item_id}/sensors/create/"
    payload = {"plant_name": plant_name, "pump_thr": pump_thr,
               "humidity": humidity, "temp": temp, "light": light}
    r = requests.post(url, json=payload)
    try:
        print("Sensor created:" if r.status_code == 201 else "Error:", r.json())
    except ValueError:
        print("Error:", r.status_code, r.text)


def update_sensor(sensor_id, **kwargs):
    """
    Update fields of an existing sensor by ID.
    Only fields provided in kwargs will be updated.
    """
    url = f"{SENSOR_BASE_URL}sensors/{sensor_id}/update/"
    r = requests.put(url, json=kwargs)
    try:
        print("Sensor updated:" if r.status_code == 200 else "Error:", r.json())
    except ValueError:
        print("Error:", r.status_code, r.text)


def delete_sensor(sensor_id):
    """
    Delete a sensor by ID.
    """
    url = f"{SENSOR_BASE_URL}sensors/{sensor_id}/delete/"
    r = requests.delete(url)
    try:
        print("Sensor deleted:" if r.status_code == 200 else "Error:", r.json())
    except ValueError:
        print("Error:", r.status_code, r.text)

# ------------------------------------------
# ITEM FUNCTIONS
# ------------------------------------------

def get_items():
    """
    Fetch and print all items (from /api/items/).
    """
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        try:
            items = response.json()
            print("Items from API:")
            for item in items:
                print(f"- {item['id']}: {item['name']} "
                      f"(Lat: {item['latitude']}, Lon: {item['longitude']})")
        except ValueError:
            print("Could not parse JSON:", response.text)
    else:
        print("Error:", response.status_code, response.text)


def create_item(name, latitude, longitude):
    """
    Create a new item with the given name, latitude, and longitude.
    """
    payload = {"name": name, "latitude": latitude, "longitude": longitude}
    response = requests.post(BASE_URL + "create/", json=payload)
    try:
        print("Item created:" if response.status_code == 201 else "Error:", response.json())
    except ValueError:
        print("Error creating item:", response.status_code, response.text)


def update_item(item_id, name=None, latitude=None, longitude=None):
    """
    Update an existing item by ID.
    Only fields that are not None will be updated.
    """
    payload = {}
    if name:
        payload["name"] = name
    if latitude:
        payload["latitude"] = latitude
    if longitude:
        payload["longitude"] = longitude

    url = f"{BASE_URL}{item_id}/update/"
    response = requests.put(url, json=payload)
    try:
        print("Item updated:" if response.status_code == 200 else "Error:", response.json())
    except ValueError:
        print("Error updating item:", response.status_code, response.text)


def delete_item(item_id):
    """
    Delete an item by ID.
    """
    url = f"{BASE_URL}{item_id}/delete/"
    response = requests.delete(url)
    try:
        print("Item deleted:" if response.status_code == 200 else "Error:", response.json())
    except ValueError:
        print("Error deleting item:", response.status_code, response.text)

# ------------------------------------------
# COMBINED FUNCTION
# ------------------------------------------

def get_all_data():
    """
    Print all items and their related sensors.
    Useful for debugging or quick overview.
    """
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        items = response.json()
        for item in items:
            print(f"Item {item['id']}: {item['name']} "
                  f"(Lat: {item['latitude']}, Lon: {item['longitude']})")

            sensors_url = f"{SENSOR_BASE_URL}items/{item['id']}/sensors/"
            r = requests.get(sensors_url)
            if r.status_code == 200:
                try:
                    sensors = r.json()
                    for s in sensors:
                        print(f"   Sensor {s['id']}: {s['plant_name']} "
                              f"(PumpThr: {s['pump_thr']}, Hum: {s['humidity']}, "
                              f"Temp: {s['temp']}, Light: {s['light']})")
                except ValueError:
                    print("   Error parsing sensors:", r.text)
            else:
                print("   Error fetching sensors:", r.status_code, r.text)
    else:
        print("Error fetching items:", response.status_code, response.text)
