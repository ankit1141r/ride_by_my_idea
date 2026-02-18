"""Open the registration test page in browser"""
import webbrowser
import time
import requests

# Check if server is running
try:
    response = requests.get("http://localhost:8001/health", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running!")
    else:
        print("⚠️ Server responded but may have issues")
except:
    print("❌ Server is not running!")
    print("\nPlease start the server first:")
    print("  python simple_app.py")
    exit(1)

# Open test page
url = "http://localhost:8001/web/test-registration.html"
print(f"\n🌐 Opening test page: {url}")
print("\nThis page will test:")
print("  1. Valid rider registration")
print("  2. Valid driver registration")
print("  3. Duplicate registration (should fail)")
print("  4. Invalid phone number (should fail)")
print("  5. Invalid email (should fail)")
print("  6. Short password (should fail)")
print("\nClick the buttons to run each test!")

time.sleep(1)
webbrowser.open(url)

print("\n✅ Test page opened in your browser!")
print("\nYou can also access:")
print(f"  Landing page: http://localhost:8001/web/index.html")
print(f"  Mobile access: http://192.168.1.3:8001/web/test-registration.html")
