#!/usr/bin/env python3
"""
Test script for the alerts API endpoints.
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BASE_URL = "https://cybersecurity-api-service-44185828496.us-central1.run.app/"  # Update this if your API is running elsewhere

def test_create_test_alerts():
    """Test creating test alerts."""
    print("\n=== Testing create test alerts ===")
    try:
        response = requests.post(f"{BASE_URL}/alerts/test/generate")
        response.raise_for_status()
        print(f"Success: {response.json()}")
        return True
    except Exception as e:
        print(f"Error creating test alerts: {e}")
        return False

def test_get_alerts():
    """Test getting all alerts."""
    print("\n=== Testing get all alerts ===")
    try:
        response = requests.get(f"{BASE_URL}/alerts/")
        response.raise_for_status()
        alerts = response.json()
        print(f"Found {len(alerts)} alerts")
        if alerts:
            print("Sample alert:", json.dumps(alerts[0], indent=2))
        return True
    except Exception as e:
        print(f"Error getting alerts: {e}")
        return False

def test_get_alert(alert_id: int):
    """Test getting a single alert by ID."""
    print(f"\n=== Testing get alert {alert_id} ===")
    try:
        response = requests.get(f"{BASE_URL}/alerts/{alert_id}")
        response.raise_for_status()
        print("Alert details:", json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error getting alert {alert_id}: {e}")
        return False

def test_update_alert_status(alert_id: int, status: str):
    """Test updating an alert's status."""
    print(f"\n=== Testing update alert {alert_id} status to {status} ===")
    try:
        response = requests.put(
            f"{BASE_URL}/alerts/{alert_id}/status",
            json={"status": status}
        )
        response.raise_for_status()
        print(f"Success: {response.json()}")
        return True
    except Exception as e:
        print(f"Error updating alert status: {e}")
        return False

def main():
    print("=== Starting Alerts API Tests ===")
    
    # Run tests
    if not test_create_test_alerts():
        print("Failed to create test alerts")
        return
    
    if not test_get_alerts():
        print("Failed to get alerts")
        return
    
    # Get the first alert ID to test with
    try:
        response = requests.get(f"{BASE_URL}/alerts/")
        response.raise_for_status()
        alerts = response.json()
        if not alerts:
            print("No alerts found to test with")
            return
        
        first_alert_id = alerts[0]['id']
        
        if not test_get_alert(first_alert_id):
            print(f"Failed to get alert {first_alert_id}")
        
        if not test_update_alert_status(first_alert_id, "in_progress"):
            print(f"Failed to update alert {first_alert_id} status")
        
        # Verify the update
        test_get_alert(first_alert_id)
        
    except Exception as e:
        print(f"Error during tests: {e}")
    
    print("\n=== Tests completed ===")

if __name__ == "__main__":
    main()
