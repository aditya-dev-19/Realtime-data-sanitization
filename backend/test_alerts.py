#!/usr/bin/env python3
"""
Test script for alert creation and formatting
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from api.alerting import (
    format_phishing_alert,
    format_code_injection_alert,
    format_sensitive_data_alert,
    format_network_anomaly_alert,
    create_alert
)

async def test_phishing_alert():
    """Test phishing alert creation"""
    print("\n🧪 Testing Phishing Alert...")
    
    # Simulate phishing detection result
    phishing_result = {
        "status": "Phishing",
        "confidence": 0.95,
        "suspicious_urls": ["http://fake-bank.com/login", "http://phishing-site.xyz"],
        "contains_urgency_keywords": True,
        "details": {
            "indicators_found": ["urgent", "click here", "verify account"]
        }
    }
    
    text = "URGENT: Your account has been compromised! Click here: http://fake-bank.com/login"
    
    # Format the alert
    alert = format_phishing_alert(text, phishing_result)
    print(f"✅ Alert formatted: {alert.title}")
    print(f"   Severity: {alert.severity}")
    print(f"   Description: {alert.description}")
    
    # Create the alert in Firestore
    result = await create_alert(alert)
    print(f"✅ Alert created: {result}")
    
    return result['status'] == 'success'

async def test_code_injection_alert():
    """Test code injection alert creation"""
    print("\n🧪 Testing Code Injection Alert...")
    
    # Simulate code injection detection result
    injection_result = {
        "status": "Injection",
        "confidence": 0.88,
        "details": {
            "patterns_found": ["<script>", "eval(", "DROP TABLE"],
            "severity": "critical"
        }
    }
    
    text = "<script>alert('XSS')</script> OR 1=1; DROP TABLE users;"
    
    # Format the alert
    alert = format_code_injection_alert(text, injection_result)
    print(f"✅ Alert formatted: {alert.title}")
    print(f"   Severity: {alert.severity}")
    print(f"   Description: {alert.description}")
    
    # Create the alert in Firestore
    result = await create_alert(alert)
    print(f"✅ Alert created: {result}")
    
    return result['status'] == 'success'

async def test_sensitive_data_alert():
    """Test sensitive data alert creation"""
    print("\n🧪 Testing Sensitive Data Alert...")
    
    # Simulate sensitive data detection result
    sensitive_result = {
        "classification": "PII",
        "confidence": 0.92,
        "has_sensitive_data": True,
        "data_types_found": ["SSN", "Credit Card", "Email"]
    }
    
    text = "My SSN is 123-45-6789 and my credit card is 4532-1234-5678-9010"
    
    # Format the alert
    alert = format_sensitive_data_alert(text, sensitive_result)
    print(f"✅ Alert formatted: {alert.title}")
    print(f"   Severity: {alert.severity}")
    print(f"   Description: {alert.description}")
    
    # Create the alert in Firestore
    result = await create_alert(alert)
    print(f"✅ Alert created: {result}")
    
    return result['status'] == 'success'

async def test_network_anomaly_alert():
    """Test network anomaly alert creation"""
    print("\n🧪 Testing Network Anomaly Alert...")
    
    # Simulate network anomaly detection result
    anomaly_result = {
        "prediction": "Anomaly",
        "reason": "Unusual traffic pattern detected"
    }
    
    features = [1.2, 3.4, 5.6, 7.8, 9.0, 2.1, 4.3, 6.5, 8.7, 0.9]
    
    # Format the alert
    alert = format_network_anomaly_alert(features, anomaly_result)
    print(f"✅ Alert formatted: {alert.title}")
    print(f"   Severity: {alert.severity}")
    print(f"   Description: {alert.description}")
    
    # Create the alert in Firestore
    result = await create_alert(alert)
    print(f"✅ Alert created: {result}")
    
    return result['status'] == 'success'

async def main():
    """Run all alert tests"""
    print("=" * 60)
    print("🚀 Starting Alert System Tests")
    print("=" * 60)
    
    tests = [
        ("Phishing Alert", test_phishing_alert),
        ("Code Injection Alert", test_code_injection_alert),
        ("Sensitive Data Alert", test_sensitive_data_alert),
        ("Network Anomaly Alert", test_network_anomaly_alert),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)