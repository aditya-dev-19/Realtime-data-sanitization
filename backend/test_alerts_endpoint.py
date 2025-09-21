import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    """Runs a series of tests against the alerts API."""
    print("=== Starting Alerts API Tests ===")

    # 1. Test the health check endpoint
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("✅ Health check passed")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return

    # 2. Test the dedicated test alert creation endpoint
    print("\n=== Testing Create Test Alerts via /test-alert ===")
    try:
        response = requests.get(f"{BASE_URL}/test-alert")
        response.raise_for_status()
        print(f"✅ Test endpoint response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create test alert via /test-alert: {e}")
        print(f"❌ Response content: {e.response.text if e.response else 'No response'}")
        return

    # 3. [MODIFIED] Test fetching the alerts (no prefix)
    print("\n=== Testing Get Alerts Endpoint ===")
    try:
        # The URL is now just /alerts/
        response = requests.get(f"{BASE_URL}/alerts/")
        response.raise_for_status()
        alerts = response.json()
        if alerts:
            print(f"✅ Successfully retrieved {len(alerts)} alerts.")
            # print(f"Latest alert: {alerts[0]}")
        else:
            print("⚠️ No alerts found, but the endpoint is working.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get alerts: {e}")
        print(f"❌ Response content: {e.response.text if e.response else 'No response'}")

if __name__ == "__main__":
    run_tests()