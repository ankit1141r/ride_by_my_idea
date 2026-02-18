"""Launch the full RideConnect project in web browser"""
import webbrowser
import time
import requests

print("=" * 70)
print("🚀 LAUNCHING RIDECONNECT - FULL PROJECT")
print("=" * 70)

# Check if server is running
print("\n📡 Checking server status...")
try:
    response = requests.get("http://localhost:8001/health", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running!")
        data = response.json()
        print(f"   Version: {data.get('version', 'N/A')}")
        print(f"   Status: {data.get('status', 'N/A')}")
    else:
        print("⚠️ Server responded but may have issues")
except:
    print("❌ Server is not running!")
    print("\n⚠️ Please start the server first:")
    print("   python simple_app.py")
    print("\nThen run this script again.")
    input("\nPress Enter to exit...")
    exit(1)

# Get platform metrics
try:
    response = requests.get("http://localhost:8001/metrics", timeout=2)
    if response.status_code == 200:
        metrics = response.json()
        print(f"\n📊 Platform Statistics:")
        print(f"   Total Users: {metrics.get('total_users', 0)}")
        print(f"   Total Rides: {metrics.get('total_rides', 0)}")
        print(f"   Active Rides: {metrics.get('active_rides', 0)}")
        print(f"   Completed Rides: {metrics.get('completed_rides', 0)}")
except:
    pass

print("\n" + "=" * 70)
print("🌐 OPENING FULL PROJECT IN YOUR BROWSER")
print("=" * 70)

# Define all pages
pages = [
    {
        "name": "Landing Page",
        "url": "http://localhost:8001/web/index.html",
        "description": "Main landing page with registration and login",
        "icon": "🏠"
    },
    {
        "name": "Navigation Hub",
        "url": "http://localhost:8001/web/navigation.html",
        "description": "Central navigation to all pages",
        "icon": "🧭"
    },
    {
        "name": "Rider Dashboard",
        "url": "http://localhost:8001/web/rider-dashboard.html",
        "description": "Book rides, view history, manage profile",
        "icon": "👤"
    },
    {
        "name": "Driver Dashboard",
        "url": "http://localhost:8001/web/driver-dashboard.html",
        "description": "Accept rides, track earnings, go online/offline",
        "icon": "🚗"
    },
    {
        "name": "Admin Panel",
        "url": "http://localhost:8001/web/admin.html",
        "description": "Manage users, monitor rides, view statistics",
        "icon": "🛡️"
    },
    {
        "name": "Animations Demo",
        "url": "http://localhost:8001/web/animations-demo.html",
        "description": "See all 40+ animations in action",
        "icon": "✨"
    },
    {
        "name": "Test Registration",
        "url": "http://localhost:8001/web/test-registration.html",
        "description": "Test registration and error handling",
        "icon": "🧪"
    },
    {
        "name": "API Documentation",
        "url": "http://localhost:8001/docs",
        "description": "Interactive API documentation (Swagger)",
        "icon": "📚"
    }
]

print("\n📄 Available Pages:\n")
for i, page in enumerate(pages, 1):
    print(f"{i}. {page['icon']} {page['name']}")
    print(f"   {page['description']}")
    print(f"   URL: {page['url']}")
    print()

print("=" * 70)
print("🚀 Opening pages in your browser...")
print("=" * 70)

# Open main landing page first
print(f"\n1. Opening Landing Page...")
webbrowser.open("http://localhost:8001/web/index.html")
time.sleep(1)

# Ask user if they want to open all pages
print("\n" + "=" * 70)
print("Would you like to open all pages in separate tabs?")
print("=" * 70)
print("\nOptions:")
print("  1. Yes - Open all pages")
print("  2. No - Just the landing page")
print("  3. Custom - Choose specific pages")

choice = input("\nEnter your choice (1/2/3): ").strip()

if choice == "1":
    print("\n🌐 Opening all pages...")
    for i, page in enumerate(pages[1:], 2):  # Skip landing page (already opened)
        print(f"{i}. Opening {page['name']}...")
        webbrowser.open(page['url'])
        time.sleep(0.5)
    print("\n✅ All pages opened!")

elif choice == "3":
    print("\n📄 Select pages to open (comma-separated numbers):")
    print("   Example: 2,3,4")
    selected = input("\nEnter page numbers: ").strip()
    
    try:
        page_nums = [int(x.strip()) for x in selected.split(",")]
        for num in page_nums:
            if 1 <= num <= len(pages):
                page = pages[num - 1]
                print(f"Opening {page['name']}...")
                webbrowser.open(page['url'])
                time.sleep(0.5)
        print("\n✅ Selected pages opened!")
    except:
        print("❌ Invalid input. Only landing page opened.")

else:
    print("\n✅ Landing page opened!")

# Display access information
print("\n" + "=" * 70)
print("📱 MOBILE ACCESS (Same WiFi Network)")
print("=" * 70)
print("\nAccess from your mobile device:")
print("  Landing Page: http://192.168.1.3:8001/web/index.html")
print("  Navigation:   http://192.168.1.3:8001/web/navigation.html")
print("  Rider:        http://192.168.1.3:8001/web/rider-dashboard.html")
print("  Driver:       http://192.168.1.3:8001/web/driver-dashboard.html")
print("  Admin:        http://192.168.1.3:8001/web/admin.html")

# Display quick tips
print("\n" + "=" * 70)
print("💡 QUICK TIPS")
print("=" * 70)
print("""
1. 📝 Register an Account:
   - Click "Sign Up" on landing page
   - Choose Rider or Driver
   - Fill in details and create account

2. 🔐 Login:
   - Click "Login" on landing page
   - Enter phone and password
   - Access your dashboard

3. 🚗 Book a Ride (Rider):
   - Login to rider dashboard
   - Enter pickup and dropoff
   - Request ride

4. 💰 Accept Rides (Driver):
   - Login to driver dashboard
   - Toggle "Go Online"
   - Accept ride requests

5. 🛡️ Admin Panel:
   - View all users and rides
   - Monitor platform statistics
   - Track revenue

6. ✨ Animations Demo:
   - See all 40+ animations
   - Interactive demonstrations
   - Hover and scroll effects
""")

# Display deployment info
print("=" * 70)
print("🚀 READY FOR DEPLOYMENT")
print("=" * 70)
print("""
Want to deploy this to a public website?

See: DEPLOYMENT_GUIDE.md

Quick Options:
  1. Railway.app (Free, 15 minutes)
  2. DigitalOcean ($6/month, 1-2 hours)
  3. AWS/Google Cloud (Enterprise, 2-4 hours)
""")

print("=" * 70)
print("✅ RIDECONNECT IS READY TO USE!")
print("=" * 70)
print("\nEnjoy your fully functional ride-hailing platform! 🚗💨")
print("\nPress Ctrl+C to exit this script (server will keep running)")

# Keep script running
try:
    input("\nPress Enter to exit...")
except KeyboardInterrupt:
    print("\n\n👋 Goodbye!")
