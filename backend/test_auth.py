import requests
import json

BASE_URL = "https://cybersecurity-api-service-44185828496.us-central1.run.app"

def test_auth_health():
    """Test if auth service is working"""
    response = requests.get(f"{BASE_URL}/auth/health")
    print(f"Auth Health: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_registration(email, password):
    """Test user registration"""
    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"Registration: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 201]

def test_login(email, password):
    """Test user login"""
    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/token", json=data)
    print(f"Login: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_debug_users():
    """Debug: Check created users"""
    response = requests.get(f"{BASE_URL}/auth/debug")
    print(f"Debug Users: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("🧪 Testing Authentication...")
    
    # Test 1: Health check
    print("\n1. Testing auth health...")
    if test_auth_health():
        print("✅ Auth service is healthy")
    else:
        print("❌ Auth service is unhealthy")
        exit(1)
    
    # Test 2: Registration
    print("\n2. Testing registration...")
    test_email = "test1@example.com"
    test_password = "testpass123"
    
    if test_registration(test_email, test_password):
        print("✅ Registration successful")
    else:
        print("❌ Registration failed")
    
    # Test 3: Check users
    print("\n3. Checking created users...")
    test_debug_users()
    
    # Test 4: Login
    print("\n4. Testing login...")
    if test_login(test_email, test_password):
        print("✅ Login successful")
    else:
        print("❌ Login failed")
    
    print("\n🏁 Authentication tests complete!")