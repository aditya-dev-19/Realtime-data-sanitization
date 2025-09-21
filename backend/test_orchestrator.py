#!/usr/bin/env python3
"""
Test script to verify the orchestrator and models are working correctly.
Run this from the backend directory: python test_orchestrator.py
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_orchestrator():
    """Test the orchestrator initialization and basic functionality"""
    print("🧪 Testing Cybersecurity Orchestrator...")
    
    try:
        # Import the orchestrator
        from api.orchestrator import CybersecurityOrchestrator
        
        # Initialize with a test model directory
        test_model_dir = "saved_models"  # Adjust this path as needed
        if not os.path.exists(test_model_dir):
            print(f"⚠️  Model directory '{test_model_dir}' doesn't exist. Creating it...")
            os.makedirs(test_model_dir, exist_ok=True)
        
        # Initialize orchestrator
        print("Initializing orchestrator...")
        orchestrator = CybersecurityOrchestrator(model_dir=test_model_dir)
        
        # Test basic functionality
        print("\n🔍 Testing basic functions...")
        
        # Test text analysis
        test_text = "Contact John Doe at john.doe@example.com or call 555-1234-5678"
        print(f"Testing text: '{test_text}'")
        
        # Test sensitive data classification
        print("\n1. Testing sensitive data classification...")
        try:
            sensitive_result = orchestrator.classify_sensitive_data(test_text)
            print(f"   Result: {sensitive_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test data quality assessment
        print("\n2. Testing data quality assessment...")
        try:
            quality_result = orchestrator.assess_data_quality(test_text)
            print(f"   Result: {quality_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test comprehensive analysis
        print("\n3. Testing comprehensive analysis...")
        try:
            comprehensive_result = orchestrator.comprehensive_analysis(test_text)
            print(f"   Result: {comprehensive_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test dynamic behavior analysis
        print("\n4. Testing dynamic behavior analysis...")
        try:
            test_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            dynamic_result = orchestrator.analyze_dynamic_behavior(test_sequence)
            print(f"   Result: {dynamic_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test network traffic analysis
        print("\n5. Testing network traffic analysis...")
        try:
            test_features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            network_result = orchestrator.analyze_network_traffic(test_features)
            print(f"   Result: {network_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test health check
        print("\n6. Testing health check...")
        try:
            health_result = orchestrator.health_check()
            print(f"   Result: {health_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test model stats
        print("\n7. Testing model stats...")
        try:
            stats_result = orchestrator.get_model_stats()
            print(f"   Result: {stats_result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n✅ Orchestrator testing completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_models():
    """Test individual model components"""
    print("\n🔧 Testing individual model components...")
    
    # Test sensitive data classifier
    print("\n1. Testing SensitiveDataClassifier...")
    try:
        from models.data_classification.sensitive_classifier import SensitiveDataClassifier
        classifier = SensitiveDataClassifier()
        
        test_text = "My email is john.doe@example.com and my phone is 555-123-4567"
        result = classifier.classify(test_text)
        print(f"   ✅ SensitiveDataClassifier works: {result.get('classification', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ SensitiveDataClassifier error: {e}")
    
    # Test data quality assessor
    print("\n2. Testing DataQualityAssessor...")
    try:
        from models.data_classification.enhanced_models import DataQualityAssessor
        assessor = DataQualityAssessor()
        
        test_data = {"name": "John", "email": "john@example.com", "age": 30}
        result = assessor.assess_json_quality(test_data)
        print(f"   ✅ DataQualityAssessor works: Score {result.get('overall_score', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ DataQualityAssessor error: {e}")
    
    # Test API interface
    print("\n3. Testing DataClassificationAPI...")
    try:
        from models.data_classification.api_interface import DataClassificationAPI
        api = DataClassificationAPI()
        
        test_text = "Contact support at support@company.com"
        result = api.classify(test_text)
        print(f"   ✅ DataClassificationAPI works: {result.get('classification', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ DataClassificationAPI error: {e}")

def create_test_models_if_needed():
    """Create test models if they don't exist"""
    print("\n🏭 Checking for test models...")
    
    model_dir = "saved_models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
    
    # List of expected model files
    expected_models = [
        "isolation_forest_model.pkl",
        "intrusion_detection_model.pkl", 
        "feature_scaler.pkl"
    ]
    
    missing_models = []
    for model_file in expected_models:
        if not os.path.exists(os.path.join(model_dir, model_file)):
            missing_models.append(model_file)
    
    if missing_models:
        print(f"   ⚠️  Missing models: {missing_models}")
        print("   💡 Creating test models...")
        try:
            # Create the models directly here instead of importing
            import numpy as np
            import joblib
            from sklearn.ensemble import IsolationForest, RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            
            # Create Network Anomaly Detector (Isolation Forest)
            print("   📦 Creating Isolation Forest...")
            anomaly_detector = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
            dummy_data = np.random.randn(1000, 10)
            anomaly_detector.fit(dummy_data)
            joblib.dump(anomaly_detector, os.path.join(model_dir, 'isolation_forest_model.pkl'))
            
            # Create Intrusion Detection System (Random Forest)
            print("   📦 Creating Random Forest...")
            intrusion_detector = RandomForestClassifier(n_estimators=100, random_state=42)
            dummy_features = np.random.randn(1000, 10)
            dummy_labels = np.random.randint(0, 5, 1000)
            intrusion_detector.fit(dummy_features, dummy_labels)
            joblib.dump(intrusion_detector, os.path.join(model_dir, 'intrusion_detection_model.pkl'))
            
            # Create Feature Scaler
            print("   📦 Creating Feature Scaler...")
            scaler = StandardScaler()
            scaler.fit(dummy_data)
            joblib.dump(scaler, os.path.join(model_dir, 'feature_scaler.pkl'))
            
            print("   ✅ Test models created successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to create test models: {e}")
            print("   💡 You may need to run manually: python api/create_test_models.py")
            return False
    else:
        print("   ✅ All required model files found!")
        return True

def main():
    """Main test function"""
    print("🚀 Starting Cybersecurity System Tests")
    print("=" * 50)
    
    # Check Python path
    print(f"Python path: {sys.path[0]}")
    print(f"Current directory: {os.getcwd()}")
    
    # Create test models if needed
    create_test_models_if_needed()
    
    # Test individual components first
    test_individual_models()
    
    # Test the main orchestrator
    success = test_orchestrator()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed! Your orchestrator should work with the API.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        print("💡 Common fixes:")
        print("   - Make sure you're in the backend directory")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Run: python -m spacy download en_core_web_sm")
        print("   - Create test models: python api/create_test_models.py")

if __name__ == "__main__":
    main()