import requests

# Base URL of your Django API
BASE_URL = "http://127.0.0.1:8000/api/items/"
CREATE_URL = "http://127.0.0.1:8000/api/items/create/"

def get_items():
    """Fetch all items from the Django API and print them"""
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        items = response.json()
        print("Items from API:")
        for item in items:
            print(f"- {item['id']}: {item['name']} "
                  f"(Lat: {item['latitude']}, Lon: {item['longitude']})")
    else:
        print("Error:", response.status_code, response.text)

def create_item(name, latitude, longitude):
    """Send a POST request to create a new item"""
    payload = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude
    }
    response = requests.post(CREATE_URL, json=payload)
    if response.status_code == 201:
        print("Item created:", response.json())
    else:
        print("Error creating item:", response.status_code, response.text)

def update_item(item_id, name=None, latitude=None, longitude=None):
    # Send a PUT request to update an existing item
    payload = {}
    if name is not None:
        payload["name"] = name
    if latitude is not None:
        payload["latitude"] = latitude
    if longitude is not None:
        payload["longitude"] = longitude

    url = f"http://127.0.0.1:8000/api/items/{item_id}/update/"
    response = requests.put(url, json=payload)
    if response.status_code == 200:
        print("Item updated:", response.json())
    else:
        print("Error updating item:", response.status_code, response.text)

def delete_item(item_id):
    # Send a DELETE request to remove an item
    url = f"http://127.0.0.1:8000/api/items/{item_id}/delete/"
    response = requests.delete(url)
    if response.status_code == 200:
        print("Item deleted:", response.json())
    else:
        print("Error deleting item:", response.status_code, response.text)



def menu():
    while True:
        print("\n--- Menu ---")
        print("1. List items")
        print("2. Create item")
        print("3. Update item")
        print("4. Delete item")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            get_items()
        elif choice == "2":
            name = input("Enter name: ")
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            create_item(name, lat, lon)
        elif choice == "3":
            item_id = int(input("Enter item ID to update: "))
            name = input("Enter new name (leave blank to skip): ")
            lat = input("Enter new latitude (leave blank to skip): ")
            lon = input("Enter new longitude (leave blank to skip): ")
            update_item(
                item_id,
                name if name else None,
                float(lat) if lat else None,
                float(lon) if lon else None
            )
        elif choice == "4":
            item_id = int(input("Enter item ID to delete: "))
            delete_item(item_id)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    menu()
