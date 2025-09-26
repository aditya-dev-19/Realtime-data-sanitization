#!/usr/bin/env python3
"""
Debug the orchestrator issue
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

def debug_orchestrator():
    """Debug the orchestrator phishing detection"""
    try:
        from api.orchestrator import CybersecurityOrchestrator

        print("🔍 Debugging Orchestrator Issue")
        print("=" * 50)

        # The exact clean text from the test
        clean_text = """
        Hello, my name is John Doe and I work as a software engineer.
        I enjoy reading technical books and writing clean code.
        My favorite programming languages are Python and JavaScript.
        """

        print(f"Clean text: {clean_text.strip()}")
        print()

        # Test with orchestrator
        model_dir = backend_dir / "downloaded_models"
        orchestrator = CybersecurityOrchestrator(model_dir=str(model_dir))

        result = orchestrator.detect_phishing(clean_text)

        print("Orchestrator result:")
        print(f"   Status: {result['status']}")
        print(f"   Confidence: {result.get('confidence', 'N/A'):.4f}")

        if 'details' in result:
            print(f"   Details: {result['details']}")

        if result['status'] == "Phishing":
            print("\n❌ ISSUE: Orchestrator is flagging clean text as phishing!")
            print("This suggests the ML model is being used instead of rule-based fallback.")
            return False
        else:
            print("\n✅ Orchestrator correctly identifies clean text as safe!")
            return True

    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_orchestrator()
    exit(0 if success else 1)
