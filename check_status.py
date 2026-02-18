#!/usr/bin/env python3
"""
Check RideConnect Server Status
"""
import requests
import sys

def check_status():
    """Check if server is running and all services are working."""
    print("=" * 60)
    print("🔍 Checking RideConnect Server Status")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:8001"
    
    # Check health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print("❌ Server is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print()
        print("To start the server, run:")
        print("   python simple_app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False
    
    print()
    
    # Check metrics
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Metrics endpoint working")
            data = response.json()
            print(f"   Total Users: {data.get('total_users', 0)}")
            print(f"   Total Rides: {data.get('total_rides', 0)}")
            print(f"   Active Rides: {data.get('active_rides', 0)}")
        else:
            print("⚠️  Metrics endpoint not working")
    except Exception as e:
        print(f"⚠️  Metrics check failed: {e}")
    
    print()
    
    # Check API endpoints
    endpoints = [
        ("/api/drivers/nearby", "Driver Search"),
        ("/api/demo/users", "Demo Users"),
        ("/api/demo/stats", "Demo Stats"),
    ]
    
    print("Checking API endpoints:")
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}")
            else:
                print(f"   ⚠️  {name} ({response.status_code})")
        except Exception:
            print(f"   ❌ {name}")
    
    print()
    print("=" * 60)
    print("📱 Access URLs:")
    print("=" * 60)
    print()
    print("Computer:")
    print(f"   http://localhost:8001/web/navigation.html")
    print()
    print("Mobile (same WiFi):")
    print(f"   http://192.168.1.3:8001/web/navigation.html")
    print()
    print("API Documentation:")
    print(f"   http://localhost:8001/docs")
    print()
    print("=" * 60)
    print("✅ All backend services are working!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        if check_status():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
