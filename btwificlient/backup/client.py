import argparse
from data_access import *  # Import all API-related functions (CRUD for items and sensors)

def main():
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

    # Call the correct function based on the selected command
    if args.command == "list":
        get_items()
    elif args.command == "create":
        create_item(args.name, args.lat, args.long)
    elif args.command == "update":
        update_item(args.id, args.name, args.lat, args.long)
    elif args.command == "delete":
        delete_item(args.id)
    elif args.command == "list-sensors":
        get_sensors(args.item_id)
    elif args.command == "create-sensor":
        create_sensor(args.item_id, args.plant, args.pump, args.hum, args.temp, args.light)
    elif args.command == "update-sensor":
        update_sensor(args.id,
                      plant_name=args.plant,
                      pump_thr=args.pump,
                      humidity=args.hum,
                      temp=args.temp,
                      light=args.light)
    elif args.command == "delete-sensor":
        delete_sensor(args.id)
    elif args.command == "dump":
        get_all_data()

# Entry point – runs the main() function when executed directly
if __name__ == "__main__":
    main()
