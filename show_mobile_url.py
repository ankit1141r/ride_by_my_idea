#!/usr/bin/env python3
"""
Show mobile access URL
"""
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to detect"

print("\n" + "=" * 70)
print("  📱 RideConnect - Mobile Access URL")
print("=" * 70 + "\n")

ip = get_local_ip()
url = f"http://{ip}:8000/web/"

print(f"Your Mobile Access URL: {url}\n")
print("Steps:")
print("1. Connect mobile to same WiFi as this computer")
print("2. Open browser on mobile")
print(f"3. Type: {url}")
print("4. Login: +919876543210 / password123\n")
print("=" * 70 + "\n")
