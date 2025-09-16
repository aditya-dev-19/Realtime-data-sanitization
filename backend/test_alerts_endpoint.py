#!/usr/bin/env python3
"""
Test script to verify the alerts API endpoints.
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
import os
BASE_URL = "http://localhost:8081"  # Update this if your API is running elsewhere

# Enable debug logging for requests
import http.client as http_client
import logging
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def test_health_check():
    """Test the health check endpoint."""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "healthy":
            print_success("Health check passed")
            return True
        else:
            print_error(f"Unexpected health status: {data}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_create_test_alerts():
    """Test creating test alerts."""
    print("\n=== Testing Create Test Alerts ===")
    try:
        # First test the test endpoint
        response = requests.get(f"{BASE_URL}/test-alert")
        response.raise_for_status()
        print_success(f"Test endpoint response: {response.json()}")
        
        # Now test creating an alert through the API
        alert_data = {
            "title": "Test Alert",
            "description": "This is a test alert",
            "severity": "MEDIUM",
            "alert_type": "SYSTEM_ALERT",
            "source": "test-script"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/alerts/",
            json=alert_data
        )
        response.raise_for_status()
        print_success(f"Successfully created test alert: {response.json()}")
        return True
    except Exception as e:
        print_error(f"Failed to create test alert: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Response content: {e.response.text}")
        return False

def test_get_alerts():
    """Test getting all alerts."""
    print("\n=== Testing Get All Alerts ===")
    try:
        response = requests.get(f"{BASE_URL}/alerts/")
        response.raise_for_status()
        alerts = response.json()
        print_success(f"Found {len(alerts)} alerts")
        if alerts:
            print("Sample alert:", json.dumps(alerts[0], indent=2))
        return True
    except Exception as e:
        print_error(f"Failed to get alerts: {e}")
        return False

def test_get_alert(alert_id: int):
    """Test getting a single alert by ID."""
    print(f"\n=== Testing Get Alert {alert_id} ===")
    try:
        response = requests.get(f"{BASE_URL}/alerts/{alert_id}")
        response.raise_for_status()
        alert = response.json()
        print_success(f"Found alert: {alert.get('title')}")
        return True
    except Exception as e:
        print_error(f"Failed to get alert {alert_id}: {e}")
        return False

def test_update_alert_status(alert_id: int, status: str):
    """Test updating an alert's status."""
    print(f"\n=== Testing Update Alert {alert_id} Status to {status} ===")
    try:
        response = requests.put(
            f"{BASE_URL}/alerts/{alert_id}/status",
            json={"status": status}
        )
        response.raise_for_status()
        data = response.json()
        print_success(f"Updated alert status: {data}")
        return True
    except Exception as e:
        print_error(f"Failed to update alert status: {e}")
        return False

def test_filter_alerts():
    """Test filtering alerts by status and severity."""
    print("\n=== Testing Filter Alerts ===")
    try:
        # Test status filter
        response = requests.get(f"{BASE_URL}/alerts/?status=open")
        response.raise_for_status()
        open_alerts = response.json()
        print_success(f"Found {len(open_alerts)} open alerts")
        
        # Test severity filter
        response = requests.get(f"{BASE_URL}/alerts/?severity=high")
        response.raise_for_status()
        high_severity = response.json()
        print_success(f"Found {len(high_severity)} high severity alerts")
        
        # Test combined filters
        response = requests.get(f"{BASE_URL}/alerts/?status=open&severity=high")
        response.raise_for_status()
        filtered = response.json()
        print_success(f"Found {len(filtered)} open high severity alerts")
        
        return True
    except Exception as e:
        print_error(f"Failed to filter alerts: {e}")
        return False

def main():
    print("=== Starting Alerts API Tests ===")
    
    # Run tests
    if not test_health_check():
        print("\n❌ Health check failed. Is the backend server running?")
        return
    
    if not test_create_test_alerts():
        print("\n❌ Failed to create test alerts")
        return
    
    if not test_get_alerts():
        print("\n❌ Failed to get alerts")
        return
    
    # Get the first alert ID to test with
    try:
        response = requests.get(f"{BASE_URL}/alerts/")
        response.raise_for_status()
        alerts = response.json()
        
        if not alerts:
            print("\n❌ No alerts found to test with")
            return
        
        first_alert_id = alerts[0]['id']
        
        if not test_get_alert(first_alert_id):
            print(f"\n❌ Failed to get alert {first_alert_id}")
        
        if not test_update_alert_status(first_alert_id, "in_progress"):
            print(f"\n❌ Failed to update alert {first_alert_id} status")
        
        if not test_filter_alerts():
            print("\n❌ Failed to filter alerts")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print_error(f"Error during tests: {e}")

if __name__ == "__main__":
    main()
