import argparse
import requests

# Base URL of your deployed Django API
BASE_URL = "https://noamnadav123.pythonanywhere.com/api/items/"

def get_items():
    """Fetch all items from the Django API and print them"""
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        try:
            items = response.json()
            print("Items from API:")
            for item in items:
                print(f"- {item['id']}: {item['name']} "
                      f"(Lat: {item['latitude']}, Lon: {item['longitude']})")
        except Exception as e:
            print("Could not parse JSON:", e)
    else:
        print("Error:", response.status_code, response.text)

def create_item(name, latitude, longitude):
    """Send a POST request to create a new item"""
    payload = {"name": name, "latitude": latitude, "longitude": longitude}
    response = requests.post(BASE_URL + "create/", json=payload)
    if response.status_code == 201:
        print("Item created:", response.json())
    else:
        print("Error creating item:", response.status_code, response.text)

def update_item(item_id, name=None, latitude=None, longitude=None):
    """Send a PUT request to update an existing item"""
    payload = {}
    if name: payload["name"] = name
    if latitude: payload["latitude"] = latitude
    if longitude: payload["longitude"] = longitude

    url = f"{BASE_URL}{item_id}/update/"
    response = requests.put(url, json=payload)
    if response.status_code == 200:
        print("Item updated:", response.json())
    else:
        print("Error updating item:", response.status_code, response.text)

def delete_item(item_id):
    """Send a DELETE request to remove an item"""
    url = f"{BASE_URL}{item_id}/delete/"
    response = requests.delete(url)
    if response.status_code == 200:
        print("Item deleted:", response.json())
    else:
        print("Error deleting item:", response.status_code, response.text)

def main():
    """  
    python client.py list
    python client.py create --name "aa" --lat 32 --long 34
    python client.py update --id 1 --name "new name"
    python client.py delete --id 1
    python client.py -h
    python client.py create -h 
    """

    parser = argparse.ArgumentParser(
        description="Client for Django API CRUD operations. "
                    "Use one of the subcommands below."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all items")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new item")
    create_parser.add_argument("--name", required=True, help="Name of the item")
    create_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    create_parser.add_argument("--long", type=float, required=True, help="Longitude")

    # update
    update_parser = subparsers.add_parser("update", help="Update an existing item")
    update_parser.add_argument("--id", type=int, required=True, help="ID of the item")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--lat", type=float, help="New latitude")
    update_parser.add_argument("--long", type=float, help="New longitude")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete an item")
    delete_parser.add_argument("--id", type=int, required=True, help="ID of the item")

    args = parser.parse_args()

    if args.command == "list":
        get_items()
    elif args.command == "create":
        create_item(args.name, args.lat, args.long)
    elif args.command == "update":
        update_item(args.id, args.name, args.lat, args.long)
    elif args.command == "delete":
        delete_item(args.id)



if __name__ == "__main__":
    main()

