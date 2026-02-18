#!/usr/bin/env python3
"""
Automatically open RideConnect website in browser
"""
import webbrowser
import time

print("=" * 60)
print("🚗 Opening RideConnect Website...")
print("=" * 60)
print()

# Open navigation page
url = "http://localhost:8001/web/navigation.html"
print(f"Opening: {url}")
webbrowser.open(url)

time.sleep(1)

print()
print("✅ Website opened in your browser!")
print()
print("📱 For Mobile Access (same WiFi):")
print("   http://192.168.1.3:8001/web/navigation.html")
print()
print("🎨 Don't miss the Animations Demo!")
print("   http://localhost:8001/web/animations-demo.html")
print()
print("=" * 60)
