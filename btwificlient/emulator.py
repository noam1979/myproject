# emulator for the sensor
import serial
import time
import random

# Configuration for the Virtual Port (Arduino side)
# Connects to the Agent via the virtual pair
EMU_PORT = 'COM20' 
BAUD_RATE = 57600 # Matches Pro Mini 8MHz speed

def run_emulator():
    try:
        # Initialize serial connection
        ser = serial.Serial(EMU_PORT, BAUD_RATE, timeout=1)
        print(f"Emulator started on {EMU_PORT}. Waiting for 'R' command...")
        
        while True:
            # Check if data is available
            if ser.in_waiting > 0:
                # Read incoming command from Agent
                command = ser.read().decode('utf-8')
                
                if command == 'R':
                    # Generate a random moisture value for testing
                    fake_humidity = random.randint(30, 85)
                    # Format: H:value (Matches the protocol we designed)
                    response = f"H:{fake_humidity}\n"
                    
                    # Send response back to Agent
                    ser.write(response.encode('utf-8'))
                    print(f"Request received. Sent Humidity: {fake_humidity}%")
            
            time.sleep(0.1) # Prevent high CPU usage
            
    except Exception as e:
        print(f"Emulator Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    run_emulator()