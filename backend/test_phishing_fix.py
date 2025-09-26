#!/usr/bin/env python3
"""
Quick test to verify the phishing detection fixes.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

def test_phishing_detection():
    """Test the phishing detection with the orchestrator."""
    try:
        from api.orchestrator import CybersecurityOrchestrator
        from rule_based_phishing import RuleBasedPhishingDetector

        print("🧪 Testing Phishing Detection Fixes")
        print("=" * 50)

        # Test with obvious phishing text
        phishing_text = """
        URGENT: Your account has been compromised!
        Click here immediately to verify your account: http://secure-bank-login.com/verify
        Account Number: 1234-5678-9012-3456
        If you don't act now, your account will be suspended!
        """

        print(f"Testing with phishing text: {phishing_text[:100]}...")

        # Test rule-based detector directly
        print("\n1. Testing Rule-Based Detector:")
        rule_detector = RuleBasedPhishingDetector()
        rule_result = rule_detector.analyze(phishing_text)
        print(f"   Status: {rule_result['status']}")
        print(f"   Confidence: {rule_result['confidence']".4f"}")
        print(f"   Indicators: {rule_result['details']['indicators_found'][:3]}...")

        # Test orchestrator
        print("\n2. Testing Orchestrator:")
        model_dir = backend_dir / "downloaded_models"
        orchestrator = CybersecurityOrchestrator(model_dir=str(model_dir))

        orch_result = orchestrator.detect_phishing(phishing_text)
        print(f"   Status: {orch_result['status']}")
        print(f"   Confidence: {orch_result.get('confidence', 'N/A')".4f"}")

        if 'details' in orch_result:
            print(f"   Details: {orch_result['details']}")

        # Test with clean text
        clean_text = "Hello, my name is John and I work as a software engineer. I enjoy reading technical books."

        print("\n3. Testing with Clean Text:")
        print(f"Testing with: {clean_text}")

        clean_result = orchestrator.detect_phishing(clean_text)
        print(f"   Status: {clean_result['status']}")
        print(f"   Confidence: {clean_result.get('confidence', 'N/A')".4f"}")

        # Check if fixes are working
        phishing_detected = (rule_result['status'] == "Phishing" and
                           orch_result['status'] == "Phishing")

        clean_safe = clean_result['status'] == "Safe"

        print("\n" + "=" * 50)
        if phishing_detected and clean_safe:
            print("✅ SUCCESS: Phishing detection is working correctly!")
            print("   - Phishing content detected")
            print("   - Clean content marked as safe")
            return True
        else:
            print("❌ ISSUES FOUND:")
            print(f"   - Phishing detected: {phishing_detected}")
            print(f"   - Clean marked safe: {clean_safe}")
            return False

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phishing_detection()
    exit(0 if success else 1)
