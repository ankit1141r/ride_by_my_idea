"""Test full registration flow including error cases"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_registration(name, phone, email, password, user_type="rider"):
    """Test user registration"""
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "name": name,
        "phone": phone,
        "email": email,
        "password": password,
        "user_type": user_type
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {user_type.upper()} Registration")
    print(f"Phone: {phone}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"User ID: {result['user']['id']}")
            print(f"Name: {result['user']['name']}")
            print(f"Token: {result['access_token'][:20]}...")
            return True
        else:
            result = response.json()
            print(f"❌ FAILED!")
            print(f"Error: {result.get('detail', result)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_login(phone, password):
    """Test user login"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "phone": phone,
        "password": password
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: LOGIN")
    print(f"Phone: {phone}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"User: {result['user']['name']}")
            print(f"Type: {result['user']['user_type']}")
            print(f"Token: {result['access_token'][:20]}...")
            return True
        else:
            result = response.json()
            print(f"❌ FAILED!")
            print(f"Error: {result.get('detail', result)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_duplicate_registration():
    """Test duplicate registration error"""
    print(f"\n{'='*60}")
    print(f"Testing: DUPLICATE REGISTRATION (Should Fail)")
    print(f"{'='*60}")
    
    # Register first time
    phone = "+919876543210"
    test_registration("First User", phone, "first@example.com", "password123", "rider")
    
    # Try to register again with same phone
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "name": "Second User",
        "phone": phone,
        "email": "second@example.com",
        "password": "password456",
        "user_type": "rider"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            print("✅ Correctly rejected duplicate!")
            print(f"Error message: {result.get('detail')}")
            return True
        else:
            print(f"❌ Should have rejected duplicate!")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_invalid_login():
    """Test invalid login credentials"""
    print(f"\n{'='*60}")
    print(f"Testing: INVALID LOGIN (Should Fail)")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "phone": "+919999999999",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            result = response.json()
            print("✅ Correctly rejected invalid credentials!")
            print(f"Error message: {result.get('detail')}")
            return True
        else:
            print(f"❌ Should have rejected invalid credentials!")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

# Run all tests
print("\n" + "="*60)
print("RIDECONNECT REGISTRATION & LOGIN TEST SUITE")
print("="*60)

results = []

# Test 1: Register a rider
results.append(("Rider Registration", test_registration(
    "Rahul Sharma",
    "+919876543211",
    "rahul@example.com",
    "password123",
    "rider"
)))

# Test 2: Register a driver
results.append(("Driver Registration", test_registration(
    "Priya Patel",
    "+919876543212",
    "priya@example.com",
    "password123",
    "driver"
)))

# Test 3: Login with rider account
results.append(("Rider Login", test_login("+919876543211", "password123")))

# Test 4: Login with driver account
results.append(("Driver Login", test_login("+919876543212", "password123")))

# Test 5: Duplicate registration
results.append(("Duplicate Registration", test_duplicate_registration()))

# Test 6: Invalid login
results.append(("Invalid Login", test_invalid_login()))

# Summary
print(f"\n{'='*60}")
print("TEST SUMMARY")
print(f"{'='*60}")

passed = sum(1 for _, result in results if result)
total = len(results)

for test_name, result in results:
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"{test_name:30} {status}")

print(f"\n{passed}/{total} tests passed")

if passed == total:
    print("\n🎉 All tests passed! Backend is working correctly!")
else:
    print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
