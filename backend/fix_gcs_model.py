#!/usr/bin/env python3
"""
Fix the models in Google Cloud Storage by uploading working versions
Run from backend directory: python fix_gcs_models.py
"""

import os
import shutil
from pathlib import Path
from google.cloud import storage
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def create_working_models_locally():
    """Create working models locally first"""
    print("🏭 Creating working models locally...")
    
    # Create a temporary directory for new models
    temp_models_dir = Path("temp_fixed_models")
    temp_models_dir.mkdir(exist_ok=True)
    
    # Model options to try (in order of preference)
    model_options = [
        "distilbert-base-uncased-finetuned-sst-2-english",
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "distilbert-base-uncased"
    ]
    
    success = False
    working_model = None
    
    for model_name in model_options:
        try:
            print(f"🔄 Trying {model_name}...")
            
            # Download tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            working_model = model_name
            success = True
            break
            
        except Exception as e:
            print(f"❌ Failed {model_name}: {e}")
            continue
    
    if not success:
        print("❌ Could not find a working base model")
        return False
    
    print(f"✅ Using {working_model} as base model")
    
    # Create phishing detection model
    try:
        print("🎣 Creating phishing detection model...")
        phishing_tokenizer = AutoTokenizer.from_pretrained(working_model)
        phishing_model = AutoModelForSequenceClassification.from_pretrained(working_model)
        
        # Set up proper labels for phishing detection
        phishing_model.config.id2label = {0: "Safe", 1: "Phishing"}
        phishing_model.config.label2id = {"Safe": 0, "Phishing": 1}
        
        # Save phishing model
        phishing_path = temp_models_dir / "phishing_model_v2"
        phishing_path.mkdir(parents=True, exist_ok=True)
        phishing_model.save_pretrained(phishing_path)
        phishing_tokenizer.save_pretrained(phishing_path)
        print(f"✅ Phishing model saved to {phishing_path}")
        
    except Exception as e:
        print(f"❌ Failed to create phishing model: {e}")
        return False
    
    # Create code injection detection model
    try:
        print("💉 Creating code injection detection model...")
        injection_tokenizer = AutoTokenizer.from_pretrained(working_model)
        injection_model = AutoModelForSequenceClassification.from_pretrained(working_model)
        
        # Set up proper labels for code injection detection
        injection_model.config.id2label = {0: "Safe", 1: "Code Injection"}
        injection_model.config.label2id = {"Safe": 0, "Code Injection": 1}
        
        # Save code injection model
        injection_path = temp_models_dir / "code_injection_model_prod"
        injection_path.mkdir(parents=True, exist_ok=True)
        injection_model.save_pretrained(injection_path)
        injection_tokenizer.save_pretrained(injection_path)
        print(f"✅ Code injection model saved to {injection_path}")
        
    except Exception as e:
        print(f"❌ Failed to create code injection model: {e}")
        return False
    
    return True

def upload_models_to_gcs():
    """Upload the fixed models to Google Cloud Storage"""
    print("\n☁️  Uploading models to Google Cloud Storage...")
    
    bucket_name = "realtime-data-sanitization-models"
    temp_models_dir = Path("temp_fixed_models")
    
    try:
        # Initialize storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Upload phishing model files
        print("🎣 Uploading phishing model...")
        phishing_dir = temp_models_dir / "phishing_model_v2"
        for file_path in phishing_dir.rglob("*"):
            if file_path.is_file():
                blob_name = f"phishing_model_v2/{file_path.name}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(str(file_path))
                print(f"   ✅ Uploaded {blob_name}")
        
        # Upload code injection model files
        print("💉 Uploading code injection model...")
        injection_dir = temp_models_dir / "code_injection_model_prod"
        for file_path in injection_dir.rglob("*"):
            if file_path.is_file():
                blob_name = f"code_injection_model_prod/{file_path.name}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(str(file_path))
                print(f"   ✅ Uploaded {blob_name}")
        
        print("✅ All models uploaded successfully to GCS!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to upload to GCS: {e}")
        return False

def clean_local_cache():
    """Clean up local cached models to force re-download"""
    print("\n🧹 Cleaning local cache...")
    
    # Remove downloaded models directory to force fresh download
    downloaded_dir = Path("downloaded_models")
    if downloaded_dir.exists():
        shutil.rmtree(downloaded_dir)
        print("✅ Removed downloaded_models directory")
    
    # Remove temporary models
    temp_dir = Path("temp_fixed_models")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("✅ Removed temp_fixed_models directory")

def test_api_after_fix():
    """Test the API after uploading fixed models"""
    print("\n🧪 Testing API after fix...")
    print("💡 Please restart your API server and then test with:")
    print()
    print("# Restart server:")
    print("uvicorn api.main:app --reload --host 0.0.0.0 --port 8080")
    print()
    print("# Test phishing detection:")
    print('curl -X POST "http://localhost:8080/detect-phishing" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"text": "Click here to win $1000000!"}\'')
    print()
    print("# Test code injection detection:")
    print('curl -X POST "http://localhost:8080/detect-code-injection" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"text": "SELECT * FROM users; DROP TABLE data;"}\'')

def main():
    """Main function"""
    print("🔧 Fix GCS Models Script")
    print("=" * 50)
    
    # Check if we have required libraries
    try:
        import torch
        import transformers
        from google.cloud import storage
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ Transformers: {transformers.__version__}")
        print("✅ Google Cloud Storage client available")
    except ImportError as e:
        print(f"❌ Missing required libraries: {e}")
        print("💡 Install with: pip install torch transformers google-cloud-storage")
        return False
    
    # Step 1: Create working models locally
    if not create_working_models_locally():
        print("❌ Failed to create working models locally")
        return False
    
    # Step 2: Upload to GCS
    if not upload_models_to_gcs():
        print("❌ Failed to upload models to GCS")
        return False
    
    # Step 3: Clean local cache
    clean_local_cache()
    
    # Step 4: Instructions for testing
    test_api_after_fix()
    
    print("\n🎉 Models fixed and uploaded to GCS!")
    print("🔄 Restart your API server to download the fixed models.")

if __name__ == "__main__":
    main()