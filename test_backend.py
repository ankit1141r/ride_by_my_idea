#!/usr/bin/env python3
"""
Test Backend API Endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unknown method: {method}")
            return False
        
        if response.status_code in [200, 201]:
            print(f"✅ {description}")
            print(f"   Status: {response.status_code}")
            if response.text:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ {description}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🧪 Testing RideConnect Backend API")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    if test_endpoint("GET", "/health", description="Health Check"):
        tests_passed += 1
    print()
    
    # Test 2: Metrics
    tests_total += 1
    if test_endpoint("GET", "/metrics", description="Platform Metrics"):
        tests_passed += 1
    print()
    
    # Test 3: Register Rider
    tests_total += 1
    rider_data = {
        "name": "Test Rider",
        "phone": "+919876543210",
        "email": "rider@test.com",
        "password": "password123",
        "user_type": "rider"
    }
    if test_endpoint("POST", "/api/auth/register", rider_data, "Register Rider"):
        tests_passed += 1
    print()
    
    # Test 4: Register Driver
    tests_total += 1
    driver_data = {
        "name": "Test Driver",
        "phone": "+919876543211",
        "email": "driver@test.com",
        "password": "password123",
        "user_type": "driver",
        "license_number": "DL1234567890",
        "vehicle_registration": "MP09AB1234",
        "vehicle_make": "Maruti",
        "vehicle_model": "Swift",
        "vehicle_color": "White"
    }
    if test_endpoint("POST", "/api/auth/register", driver_data, "Register Driver"):
        tests_passed += 1
    print()
    
    # Test 5: Login
    tests_total += 1
    login_data = {
        "phone": "+919876543210",
        "password": "password123"
    }
    if test_endpoint("POST", "/api/auth/login", login_data, "User Login"):
        tests_passed += 1
    print()
    
    # Test 6: Request Ride
    tests_total += 1
    ride_data = {
        "pickup_location": "Rajwada, Indore",
        "dropoff_location": "Treasure Island Mall, Indore",
        "pickup_lat": 22.7196,
        "pickup_lon": 75.8577,
        "dropoff_lat": 22.7532,
        "dropoff_lon": 75.8937
    }
    if test_endpoint("POST", "/api/rides/request", ride_data, "Request Ride"):
        tests_passed += 1
    print()
    
    # Test 7: Get Nearby Drivers
    tests_total += 1
    if test_endpoint("GET", "/api/drivers/nearby", description="Get Nearby Drivers"):
        tests_passed += 1
    print()
    
    # Test 8: Get Ride History
    tests_total += 1
    if test_endpoint("GET", "/api/rides/history", description="Get Ride History"):
        tests_passed += 1
    print()
    
    # Test 9: Admin Stats
    tests_total += 1
    if test_endpoint("GET", "/api/admin/stats", description="Get Admin Stats"):
        tests_passed += 1
    print()
    
    # Test 10: Get All Users
    tests_total += 1
    if test_endpoint("GET", "/api/admin/users", description="Get All Users"):
        tests_passed += 1
    print()
    
    # Summary
    print("=" * 60)
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed")
    if tests_passed == tests_total:
        print("✅ All backend services are working!")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed")
    print("=" * 60)

if __name__ == "__main__":
    main()
