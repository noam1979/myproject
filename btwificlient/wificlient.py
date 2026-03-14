import subprocess
import re
import socket

# Function to get the SSID the computer is currently connected to
def get_current_ssid():
    try:
        # Check WiFi interface details on Windows
        results = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode('ascii', errors='ignore')
        for line in results.split('\n'):
            if "SSID" in line and "BSSID" not in line:
                return line.split(":")[1].strip()
    except Exception:
        # Return Not Connected if command fails
        return "Not Connected"
    return "Unknown"

# Function to scan the network and return a dictionary of devices
def scan_network():
    current_ssid = get_current_ssid()
    
    # Get the local ARP table (works without winpcap)
    try:
        output = subprocess.check_output(("arp", "-a")).decode('ascii', errors='ignore')
    except Exception as e:
        print(f"Error running ARP: {e}")
        return {}

    devices_dict = {}
    
    # Regex pattern to extract IP and MAC addresses
    pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+([-0-9a-fA-F]{17})\s+(\w+)")
    
    for line in output.split('\n'):
        match = pattern.search(line)
        if match:
            ip = match.group(1)
            mac = match.group(2).replace('-', ':').upper()
            
            # Filter out broadcast and multicast addresses
            if mac.startswith("FF:FF") or ip.startswith("224.") or ip.startswith("239."):
                continue

            # Try to resolve the device Name (hostname)
            try:
                name = socket.gethostbyaddr(ip)[0]
            except (socket.herror, socket.gaierror):
                name = "Unknown"

            # Determine Role: Typically .1 is the Access Point/Gateway
            role = "AP" if ip.endswith(".1") else "Client"
            
            # Store everything in the dictionary using MAC as the key
            devices_dict[mac] = {
                "name": name,
                "ip": ip,
                "role": role,
                "ssid": current_ssid
            }
    
    return devices_dict

# Main execution block
if __name__ == "__main__":
    print("Scanning Network Devices...")
    results = scan_network()

    # Define table header
    header = f"{'MAC Address':<20} {'IP Address':<15} {'Role':<10} {'SSID':<15} {'Name'}"
    print(header)
    print("-" * len(header))

    # Iterate through the dictionary and print values
    for mac, info in results.items():
        # Corrected f-string formatting
        print(f"{mac:<20} {info['ip']:<15} {info['role']:<10} {info['ssid']:<15} {info['name']}")

    # Final verification of the dictionary object
    # print("\nFinal Dictionary:", results)