import socket

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

ips = ["192.168.10.144", "192.168.10.1"]  # replace with your IPs
for ip in ips:
    name = get_hostname(ip)
    print(f"{ip} -> {name if name else 'No hostname'}")
