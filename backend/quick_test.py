#!/usr/bin/env python3
"""
Quick test script for your cybersecurity system
Run from backend directory: python quick_test.py
"""

import os
import sys
from pathlib import Path

def test_orchestrator():
    """Test the orchestrator"""
    print("🧪 Testing Cybersecurity Orchestrator...")
    
    try:
        # Import the orchestrator
        from api.orchestrator import CybersecurityOrchestrator
        print("✅ Orchestrator imported successfully")
        
        # Create models directory if it doesn't exist
        models_dir = "saved_models"
        os.makedirs(models_dir, exist_ok=True)
        
        # Initialize orchestrator
        print("🚀 Initializing orchestrator...")
        orchestrator = CybersecurityOrchestrator(model_dir=models_dir)
        print("✅ Orchestrator initialized successfully")
        
        # Test basic functionality
        print("\n🔍 Testing basic functions...")
        
        # Test 1: Sensitive data classification
        test_text = "Contact John Doe at john.doe@example.com or call 555-1234-5678"
        print(f"Testing text: '{test_text[:50]}...'")
        
        try:
            sensitive_result = orchestrator.classify_sensitive_data(test_text)
            classification = sensitive_result.get('classification', 'Unknown')
            print(f"📧 Sensitive Data Classification: {classification}")
        except Exception as e:
            print(f"❌ Sensitive data classification failed: {e}")
        
        # Test 2: Data quality assessment  
        try:
            quality_result = orchestrator.assess_data_quality(test_text)
            quality_score = quality_result.get('quality_score', 'Unknown')
            print(f"📊 Data Quality Score: {quality_score}")
        except Exception as e:
            print(f"❌ Data quality assessment failed: {e}")
        
        # Test 3: Dynamic behavior analysis
        try:
            test_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            dynamic_result = orchestrator.analyze_dynamic_behavior(test_sequence)
            status = dynamic_result.get('status', 'Unknown')
            print(f"🔒 Dynamic Behavior Analysis: {status}")
        except Exception as e:
            print(f"❌ Dynamic behavior analysis failed: {e}")
        
        # Test 4: Network traffic analysis (only if models exist)
        try:
            test_features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            network_result = orchestrator.analyze_network_traffic(test_features)
            if 'error' in network_result:
                print(f"⚠️  Network Traffic Analysis: {network_result['error']}")
            else:
                print(f"🌐 Network Traffic Analysis: OK")
        except Exception as e:
            print(f"❌ Network traffic analysis failed: {e}")
        
        # Test 5: Health check
        try:
            health_result = orchestrator.health_check()
            orchestrator_status = health_result.get('orchestrator', 'Unknown')
            print(f"🏥 Health Check - Orchestrator: {orchestrator_status}")
            
            # Show which components are working
            for component, status in health_result.items():
                if component != 'orchestrator':
                    print(f"   - {component}: {status}")
                    
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        print("\n✅ Orchestrator testing completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the backend directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_models():
    """Check if basic models exist"""
    print("\n📁 Checking for model files...")
    
    models_dir = Path("saved_models")
    if not models_dir.exists():
        print("⚠️  saved_models directory doesn't exist")
        print("💡 Run: python api/create_test_models.py")
        return False
    
    required_models = [
        "isolation_forest_model.pkl",
        "intrusion_detection_model.pkl",
        "feature_scaler.pkl"
    ]
    
    missing_models = []
    for model_file in required_models:
        if (models_dir / model_file).exists():
            print(f"✅ {model_file}")
        else:
            print(f"❌ {model_file} - MISSING")
            missing_models.append(model_file)
    
    if missing_models:
        print(f"\n💡 To create missing models, run:")
        print("   python api/create_test_models.py")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Quick Cybersecurity System Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api").exists():
        print("❌ Please run this from the backend directory")
        print("   (The directory should contain the 'api' folder)")
        return False
    
    print(f"📂 Working directory: {Path.cwd()}")
    
    # Check for models (optional)
    models_exist = check_models()
    if not models_exist:
        print("⚠️  Some models are missing, but we'll continue testing...")
    
    # Test the orchestrator
    success = test_orchestrator()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Basic tests completed successfully!")
        print("💡 Your orchestrator should work. Try starting the API:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8080")
    else:
        print("❌ Some tests failed. Check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()