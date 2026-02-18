"""Open all RideConnect pages in browser"""
import webbrowser
import time
import requests

print("=" * 70)
print("🚀 RIDECONNECT - OPENING ALL PAGES")
print("=" * 70)

# Check server
print("\n📡 Checking server...")
try:
    response = requests.get("http://localhost:8001/health", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running!")
    else:
        print("⚠️ Server may have issues")
except:
    print("❌ Server not running! Start with: python simple_app.py")
    exit(1)

# Get stats
try:
    response = requests.get("http://localhost:8001/metrics", timeout=2)
    if response.status_code == 200:
        metrics = response.json()
        print(f"\n📊 Platform Stats:")
        print(f"   Users: {metrics.get('total_users', 0)}")
        print(f"   Rides: {metrics.get('total_rides', 0)}")
except:
    pass

print("\n" + "=" * 70)
print("🌐 OPENING ALL PAGES IN YOUR BROWSER")
print("=" * 70)

pages = [
    ("🏠 Landing Page", "http://localhost:8001/web/index.html"),
    ("🧭 Navigation Hub", "http://localhost:8001/web/navigation.html"),
    ("👤 Rider Dashboard", "http://localhost:8001/web/rider-dashboard.html"),
    ("🚗 Driver Dashboard", "http://localhost:8001/web/driver-dashboard.html"),
    ("🛡️ Admin Panel", "http://localhost:8001/web/admin.html"),
    ("✨ Animations Demo", "http://localhost:8001/web/animations-demo.html"),
    ("🧪 Test Registration", "http://localhost:8001/web/test-registration.html"),
    ("📚 API Documentation", "http://localhost:8001/docs"),
]

for i, (name, url) in enumerate(pages, 1):
    print(f"\n{i}. Opening {name}...")
    print(f"   {url}")
    webbrowser.open(url)
    time.sleep(0.5)

print("\n" + "=" * 70)
print("✅ ALL PAGES OPENED!")
print("=" * 70)

print("\n📱 Mobile Access (Same WiFi):")
print("   http://192.168.1.3:8001/web/index.html")

print("\n💡 Quick Tips:")
print("   • Register: Click 'Sign Up' on landing page")
print("   • Login: Use your phone number and password")
print("   • Book Ride: Login as rider, enter locations")
print("   • Accept Rides: Login as driver, go online")
print("   • Admin: View all users and statistics")

print("\n🚀 Deployment:")
print("   See DEPLOYMENT_GUIDE.md for instructions")

print("\n" + "=" * 70)
print("🎉 ENJOY YOUR RIDECONNECT PLATFORM!")
print("=" * 70)
