"""Test registration endpoint"""
import requests
import json

# Test registration
url = "http://localhost:8001/api/auth/register"
data = {
    "name": "Test User",
    "phone": "+919999999999",
    "email": "test@example.com",
    "password": "password123",
    "user_type": "rider"
}

print("Testing registration endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
