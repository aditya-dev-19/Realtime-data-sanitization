#!/usr/bin/env python3
"""
Debug the clean text issue
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

def debug_clean_text():
    """Debug why clean text is being flagged as phishing"""
    try:
        from rule_based_phishing import RuleBasedPhishingDetector

        print("🔍 Debugging Clean Text Issue")
        print("=" * 50)

        # The exact clean text from the test
        clean_text = """
        Hello, my name is John Doe and I work as a software engineer.
        I enjoy reading technical books and writing clean code.
        My favorite programming languages are Python and JavaScript.
        """

        print(f"Clean text: {clean_text.strip()}")
        print()

        # Test with rule-based detector
        detector = RuleBasedPhishingDetector()
        result = detector.analyze(clean_text)

        print("Rule-based detector result:")
        print(f"   Status: {result['status']}")
        print(f"   Confidence: {result['confidence']:.4f}")
        print(f"   Indicators: {result['details']['indicators_found']}")

        if result['status'] == "Phishing":
            print("\n❌ ISSUE: Clean text is being flagged as phishing!")
            print("This suggests there are still keywords or patterns triggering detection.")
            return False
        else:
            print("\n✅ Clean text is correctly identified as safe!")
            return True

    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_clean_text()
    exit(0 if success else 1)
