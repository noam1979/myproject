# agent.py
import serial
import time
import argparse
from data_access import DjangoAPIClient, USERNAME, PASSWORD, LOGIN_URL

# --- CONFIGURATION ---
SERIAL_PORT = 'COM7'
BAUD_RATE = 9600
ITEM_ID = 22           # Your Gateway ID in Givat HaShlosha
POLL_INTERVAL = 5      # Seconds between updates

def main():
    # 1. Initialize Django Client
    client = DjangoAPIClient(USERNAME, PASSWORD, LOGIN_URL)
    if not client.is_authenticated:
        print("Failed to authenticate with Django. Exiting.")
        return

    # 2. Initialize Serial Connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        # Wait for Arduino to stabilize after connection reset
        time.sleep(2) 
        print(f"Connected to Arduino on {SERIAL_PORT}")
    except Exception as e:
        print(f"Serial Error: {e}")
        return

    # --- STARTUP HANDSHAKE: FIND THE CORRECT SENSOR ---
    print("Syncing with Django and searching for hardware...")
    
    # Fetch all sensors for this gateway
    all_web_sensors = client.get_sensors(ITEM_ID)
    if not all_web_sensors:
        print(f"No sensors found for Item {ITEM_ID} in Django.")
        return

    active_sensor_id = None
    active_sn = None

    # Loop through all sensors in the DB to see which one is plugged in
    for sensor in all_web_sensors:
        sn_to_test = str(sensor.get('sn'))
        print(f"Testing for Hardware SN: {sn_to_test}...")
        
        # Send addressable request, e.g., "R1"
        ser.write(f"R{sn_to_test}\n".encode('utf-8'))
        time.sleep(0.5)
        
        response = ser.readline().decode('utf-8').strip()
        
        # Check if response matches: "SN:1;P:..."
        if response.startswith(f"SN:{sn_to_test}"):
            print(f"Found Match! Hardware SN {sn_to_test} is Sensor ID {sensor['id']} ({sensor['plant_name']})")
            active_sensor_id = sensor['id']
            active_sn = sn_to_test
            break

    if not active_sensor_id:
        print("No matching hardware SN found on this port. Check Arduino SN or Django settings.")
        ser.close()
        return

    # --- MAIN LOOP ---
    last_web_threshold = None
    print(f"Agent started for SN:{active_sn}. Press Ctrl+C to stop.")

    try:
        while True:
            # STEP A: Check Web for threshold changes
            sensor_data = client.get_sensor_details(ITEM_ID, active_sensor_id)
            if sensor_data:
                # Use int conversion as requested
                current_web_threshold = int(float(sensor_data.get('pump_thr', 50)))
                
                if current_web_threshold != last_web_threshold:
                    # Send addressable Set command: "S1 45"
                    print(f"New web threshold: {current_web_threshold}. Sending S{active_sn}...")
                    ser.write(f"S{active_sn} {current_web_threshold}\n".encode('utf-8'))
                    time.sleep(0.5)

                    # Verify update immediately using "R1"
                    ser.write(f"R{active_sn}\n".encode('utf-8'))
                    verify_line = ser.readline().decode('utf-8').strip()
                    print(f"Get {verify_line}")
                    
                    if f"P:{current_web_threshold}" in verify_line:
                        last_web_threshold = current_web_threshold
                    else:
                        print("Verification mismatch. Will retry next cycle.")

            # STEP B: Regular update of sensor values (Humidity, Temp, Light)
            ser.write(f"R{active_sn}\n".encode('utf-8'))
            line = ser.readline().decode('utf-8').strip()
            
            if line.startswith(f"SN:{active_sn}"):
                try:
                    # Parse string like: SN:1;P:50;H:70;T:24;L:500
                    parts = dict(item.split(":") for item in line.split(";") if ":" in item)
                    
                    # Update Django with integers
                    client.update_sensor(
                        sensor_id=active_sensor_id,
                        humidity=int(float(parts.get('H', 0))),
                        temp=int(float(parts.get('T', 0))),
                        light=int(float(parts.get('L', 0)))
                    )
                except Exception as e:
                    print(f"Parsing error: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nAgent stopped.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()