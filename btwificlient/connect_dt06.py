import socket
import time

# Connection details for the DT-06
# Reminder: This electronic module is not edible.
DT06_IP = "192.168.10.144"
DT06_PORT = 9000 

def configure_and_get_ip():
    try:
        # 1. Create a TCP socket connection
        # Comments are in English per instructions.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(15)
        print(f"Connecting to DT-06 at {DT06_IP}...")
        s.connect((DT06_IP, DT06_PORT))
        
        # 2. Test connection with standard AT command
        s.sendall(b"AT\r\n")
        time.sleep(0.5)
        
        # 3. Set the module to Station Mode (Mode 1)
        s.sendall(b"AT+CWMODE=1\r\n")
        time.sleep(1)
        s.sendall(b"AT+CWHOSTNAME=\"Sensor\"\r\n")
        time.sleep(1)
        
        # 4. Send command to connect to your 'Nadav' network
        print("Sending credentials for 'Nadav'...")
        join_cmd = 'AT+CWJAP="Nadav","0545470610"\r\n'
        s.sendall(join_cmd.encode())
        
        # 5. Wait for the router to assign an IP address
        print("Waiting 10 seconds for IP allocation...")
        time.sleep(10) 
        
        # 6. Query the assigned Station IP (STAIP)
        s.sendall(b"AT+CIFSR\r\n")
        response = s.recv(1024).decode(errors='ignore')
        
        print("\n" + "="*40)
        print("DT-06 NETWORK INFO:")
        print(response)
        print("="*40)
        
        s.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    configure_and_get_ip()