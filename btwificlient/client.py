# client/client.py
# if i want to test the WEB with switches
import argparse
import json
# Import the client class and configuration variables
from data_access import DjangoAPIClient, USERNAME, PASSWORD, LOGIN_URL


def get_all_data(client):
    """
    Fetches and prints all items and their related sensors using the authenticated client.
    """
    # Check if the client successfully logged in
    if not client.is_authenticated:
        print("Aborting data fetch because client failed to authenticate.")
        return

    # Use the client object's method to fetch all items
    items = client.get_items()
    
    if not items:
        print("No items found or error occurred while fetching items.")
        return

    print("--- Successful Data Dump ---")
    
    for item in items:
        # Print item details
        print(f"Item {item['id']}: {item['name']} "
              f"(Lat: {item['latitude']}, Lon: {item['longitude']})")

        # Use the client object's method to fetch sensors for the current item
        sensors = client.get_sensors(item['id'])
        
        if sensors:
            for s in sensors:
                # Print sensor details
                print(f"    Sensor {s['id']}: {s['plant_name']} "
                      f"(PumpThr: {s['pump_thr']}, Hum: {s['humidity']}, "
                      f"Temp: {s['temp']}, Light: {s['light']})")
        else:
            print("    No sensors found or error fetching sensors.")


def main():
    # 1. Initialize the client (this automatically attempts to log in)
    client = DjangoAPIClient(USERNAME, PASSWORD, LOGIN_URL)

    # Check if login was successful before continuing to parse commands
    if not client.is_authenticated:
        # If authentication fails, the data_access handles printing the error, we just exit main.
        return

    # Create the main argument parser for the CLI tool
    parser = argparse.ArgumentParser(
        description="Client for Django API CRUD operations."
    )

    # Create a group of subcommands (like: list, create, update, etc.)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -----------------------------
    # Item commands
    # -----------------------------

    # List all items
    subparsers.add_parser("list", help="List all items")

    # Create a new item
    create_parser = subparsers.add_parser("create", help="Create a new item")
    create_parser.add_argument("--name", required=True, help="Item name")
    create_parser.add_argument("--lat", type=float, required=True, help="Item latitude")
    create_parser.add_argument("--long", type=float, required=True, help="Item longitude")

    # Update an existing item
    update_parser = subparsers.add_parser("update", help="Update an item")
    update_parser.add_argument("--id", type=int, required=True, help="Item ID to update")
    update_parser.add_argument("--name", help="New name for the item")
    update_parser.add_argument("--lat", type=float, help="New latitude")
    update_parser.add_argument("--long", type=float, help="New longitude")

    # Delete an item by ID
    delete_parser = subparsers.add_parser("delete", help="Delete an item")
    delete_parser.add_argument("--id", type=int, required=True, help="Item ID to delete")

    # -----------------------------
    # Sensor commands
    # -----------------------------

    # List all sensors belonging to a specific item
    list_sensors = subparsers.add_parser("list-sensors", help="List sensors for an item")
    list_sensors.add_argument("--item-id", type=int, required=True, help="Item ID to list sensors for")

    # Create a new sensor under a specific item
    create_sensor_parser = subparsers.add_parser("create-sensor", help="Create a sensor")
    create_sensor_parser.add_argument("--item-id", type=int, required=True, help="Item ID the sensor belongs to")
    create_sensor_parser.add_argument("--plant", required=True, help="Plant name linked to the sensor")
    create_sensor_parser.add_argument("--pump", type=float, default=50, help="Pump threshold (default 50)")
    create_sensor_parser.add_argument("--hum", type=float, default=0, help="Humidity value (default 0)")
    create_sensor_parser.add_argument("--temp", type=float, default=0, help="Temperature value (default 0)")
    create_sensor_parser.add_argument("--light", type=float, default=0, help="Light value (default 0)")

    # Update an existing sensor
    update_sensor_parser = subparsers.add_parser("update-sensor", help="Update a sensor")
    update_sensor_parser.add_argument("--id", type=int, required=True, help="Sensor ID to update")
    update_sensor_parser.add_argument("--plant", help="New plant name")
    update_sensor_parser.add_argument("--pump", type=float, help="New pump threshold")
    update_sensor_parser.add_argument("--hum", type=float, help="New humidity value")
    update_sensor_parser.add_argument("--temp", type=float, help="New temperature value")
    update_sensor_parser.add_argument("--light", type=float, help="New light value")

    # Delete a sensor by ID
    delete_sensor_parser = subparsers.add_parser("delete-sensor", help="Delete a sensor")
    delete_sensor_parser.add_argument("--id", type=int, required=True, help="Sensor ID to delete")

    # Dump all items and sensors (show full data)
    subparsers.add_parser("dump", help="List all items and sensors")

    # Parse the command-line arguments
    args = parser.parse_args()

    # -----------------------------
    # Command execution
    # -----------------------------

    # Call the correct function based on the selected command, using the client object
    if args.command == "list":
        # Get items and format the printout
        items = client.get_items()
        if items:
            print("Items from API:")
            for item in items:
                print(f"- {item['id']}: {item['name']} "
                      f"(Lat: {item['latitude']}, Lon: {item['longitude']})")
    elif args.command == "create":
        client.create_item(args.name, args.lat, args.long)
    elif args.command == "update":
        # Pass all update arguments, allowing None for fields not provided
        client.update_item(args.id, args.name, args.lat, args.long)
    elif args.command == "delete":
        client.delete_item(args.id)
    elif args.command == "list-sensors":
        # Get sensors and format the printout
        sensors = client.get_sensors(args.item_id)
        if sensors:
            print(f"Sensors for item {args.item_id}:")
            for s in sensors:
                print(f"- {s['id']}: {s['plant_name']} "
                      f"(PumpThr: {s['pump_thr']}, Hum: {s['humidity']}, "
                      f"Temp: {s['temp']}, Light: {s['light']})")
    elif args.command == "create-sensor":
        client.create_sensor(args.item_id, args.plant, args.pump, args.hum, args.temp, args.light)
    elif args.command == "update-sensor":
        # Collect kwargs for sensor update, allowing None/default values to be skipped
        update_kwargs = {}
        if args.plant:
            update_kwargs['plant_name'] = args.plant
        if args.pump is not None:
            update_kwargs['pump_thr'] = args.pump
        if args.hum is not None:
            update_kwargs['humidity'] = args.hum
        if args.temp is not None:
            update_kwargs['temp'] = args.temp
        if args.light is not None:
            update_kwargs['light'] = args.light
        
        client.update_sensor(args.id, **update_kwargs)
        
    elif args.command == "delete-sensor":
        client.delete_sensor(args.id)
    elif args.command == "dump":
        get_all_data(client)

# Entry point – runs the main() function when executed directly
if __name__ == "__main__":
    main()