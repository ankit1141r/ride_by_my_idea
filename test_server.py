import requests
import json

def test_server():
    base_url = "http://localhost:8001"
    
    print("🧪 Testing RideConnect Server")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test demo users endpoint
    try:
        response = requests.get(f"{base_url}/api/demo/users")
        print(f"✅ Demo Users: {response.status_code}")
        users = response.json()
        print(f"   Found {len(users['users'])} users")
    except Exception as e:
        print(f"❌ Demo Users Failed: {e}")
    
    # Test demo rides endpoint
    try:
        response = requests.get(f"{base_url}/api/demo/rides")
        print(f"✅ Demo Rides: {response.status_code}")
        rides = response.json()
        print(f"   Found {len(rides['rides'])} rides")
    except Exception as e:
        print(f"❌ Demo Rides Failed: {e}")
    
    # Test demo stats endpoint
    try:
        response = requests.get(f"{base_url}/api/demo/stats")
        print(f"✅ Demo Stats: {response.status_code}")
        stats = response.json()
        print(f"   Total Users: {stats['total_users']}")
        print(f"   Total Rides: {stats['total_rides']}")
        print(f"   Revenue: ₹{stats['total_revenue']}")
    except Exception as e:
        print(f"❌ Demo Stats Failed: {e}")
    
    print("\n🌐 Access Points:")
    print(f"   Web Interface: {base_url}/web/")
    print(f"   API Documentation: {base_url}/docs")
    print(f"   Health Check: {base_url}/health")

if __name__ == "__main__":
    test_server()