#!/usr/bin/env python3
"""
Test script to verify the false positive fix for code injection alerts
"""
import requests
import json

def test_clean_text():
    """Test clean text that was causing false positives"""
    clean_texts = [
        "Hello, I hope you're having a great day! I just finished reading an interesting article about artificial intelligence and machine learning. The weather is beautiful today - perfect for a walk in the park. Looking forward to our meeting tomorrow at 2 PM.",
        "Project update: All tests are passing. Code review completed successfully. Ready for deployment.",
        "Thank you for your email. I will review the document and get back to you by end of day."
    ]
    
    base_url = "http://localhost:8000"
    
    for i, text in enumerate(clean_texts, 1):
        print(f"\n🧪 Test {i}: Clean Text Analysis")
        print(f"Text: {text[:100]}...")
        
        try:
            response = requests.post(
                f"{base_url}/comprehensive-analysis",
                data={"text": text},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                alerts_created = data.get("alerts_created", [])
                risk_score = data.get("overall_risk_score", 0)
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Risk Score: {risk_score:.3f}")
                print(f"🚨 Alerts Created: {alerts_created}")
                
                # Check code injection result
                code_injection = data.get("results", {}).get("code_injection", {})
                status = code_injection.get("status", "Unknown")
                confidence = code_injection.get("confidence", 0)
                print(f"💉 Code Injection: {status} (confidence: {confidence:.3f})")
                
                if "code_injection" in alerts_created:
                    print("❌ FAIL: Code injection alert created for clean text!")
                    return False
                else:
                    print("✅ PASS: No false positive code injection alert")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    return True

def test_malicious_text():
    """Test that real malicious content still triggers alerts"""
    malicious_text = "<script>alert('XSS Attack!')</script> OR 1=1; DROP TABLE users; --"
    
    print("Test: Malicious Content Detection")
    print(f"Text: {malicious_text}")
    
    try:
        response = requests.post(
            "http://localhost:8000/comprehensive-analysis",
            data={"text": malicious_text},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            alerts_created = data.get("alerts_created", [])
            risk_score = data.get("overall_risk_score", 0)
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Risk Score: {risk_score:.3f}")
            print(f"🚨 Alerts Created: {alerts_created}")
            
            if "code_injection" in alerts_created:
                print("✅ PASS: Legitimate code injection detected!")
                return True
            else:
                print("❌ FAIL: Real code injection not detected!")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Code Injection False Positive Fix")
    print("=" * 60)
    
    # Test 1: Clean text should NOT create alerts
    clean_ok = test_clean_text()
    
    # Test 2: Malicious text SHOULD create alerts
    malicious_ok = test_malicious_text()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if clean_ok and malicious_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ False positive fix is working correctly")
        print("✅ Legitimate threats still detected")
        exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Fix needs more work before deployment")
        exit(1)