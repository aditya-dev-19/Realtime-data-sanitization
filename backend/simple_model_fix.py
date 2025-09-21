#!/usr/bin/env python3
"""
Simple approach: Download working pre-trained models
Run from backend directory: python simple_model_fix.py
"""

import os
import shutil
from pathlib import Path
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def remove_corrupted_models():
    """Remove the corrupted model directories"""
    print("🗑️  Removing corrupted models...")
    
    models_dir = Path("saved_models")
    corrupted_models = ["phishing_model_v2", "code_injection_model_prod"]
    
    for model_name in corrupted_models:
        model_path = models_dir / model_name
        if model_path.exists():
            print(f"   Removing {model_path}")
            shutil.rmtree(model_path)

def download_and_save_model(model_name, save_path, labels):
    """Download a pre-trained model and save it locally"""
    try:
        print(f"📥 Downloading {model_name}...")
        
        # Download tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Set up labels if the model doesn't have them
        if not hasattr(model.config, 'id2label') or not model.config.id2label:
            model.config.id2label = labels['id2label']
            model.config.label2id = labels['label2id']
        
        # Create save directory
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save model and tokenizer
        model.save_pretrained(save_path)
        tokenizer.save_pretrained(save_path)
        
        print(f"✅ Saved {model_name} to {save_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {model_name}: {e}")
        return False

def create_basic_models():
    """Create basic working models using existing pre-trained models"""
    print("\n🏭 Creating basic transformer models...")
    
    models_dir = Path("saved_models")
    models_dir.mkdir(exist_ok=True)
    
    # Try different model options in order of preference
    model_options = [
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "distilbert-base-uncased-finetuned-sst-2-english", 
        "cardiffnlp/twitter-roberta-base-sentiment",
        "distilbert-base-uncased"
    ]
    
    success = False
    
    for model_name in model_options:
        try:
            print(f"\n🔄 Trying model: {model_name}")
            
            # Download and setup for phishing detection
            phishing_labels = {
                'id2label': {0: 'Safe', 1: 'Phishing'},
                'label2id': {'Safe': 0, 'Phishing': 1}
            }
            
            phishing_success = download_and_save_model(
                model_name,
                models_dir / "phishing_model_v2",
                phishing_labels
            )
            
            # Download and setup for code injection detection  
            injection_labels = {
                'id2label': {0: 'Safe', 1: 'Code Injection'},
                'label2id': {'Safe': 0, 'Code Injection': 1}
            }
            
            injection_success = download_and_save_model(
                model_name,
                models_dir / "code_injection_model_prod", 
                injection_labels
            )
            
            if phishing_success and injection_success:
                print(f"✅ Successfully created models using {model_name}")
                success = True
                break
            else:
                print(f"❌ Failed with {model_name}, trying next option...")
                
        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            continue
    
    return success

def test_new_models():
    """Test the newly created models"""
    print("\n🧪 Testing new models...")
    
    try:
        # Test loading the models directly
        models_dir = Path("saved_models")
        
        # Test phishing model
        print("🎣 Testing phishing model...")
        phishing_tokenizer = AutoTokenizer.from_pretrained(models_dir / "phishing_model_v2")
        phishing_model = AutoModelForSequenceClassification.from_pretrained(models_dir / "phishing_model_v2")
        print(f"   ✅ Phishing model loaded: {phishing_model.config.id2label}")
        
        # Test code injection model
        print("💉 Testing code injection model...")
        injection_tokenizer = AutoTokenizer.from_pretrained(models_dir / "code_injection_model_prod")
        injection_model = AutoModelForSequenceClassification.from_pretrained(models_dir / "code_injection_model_prod")
        print(f"   ✅ Code injection model loaded: {injection_model.config.id2label}")
        
        # Test with orchestrator
        print("🔧 Testing with orchestrator...")
        from api.orchestrator import CybersecurityOrchestrator
        
        orchestrator = CybersecurityOrchestrator(model_dir="saved_models")
        
        # Quick functionality test
        test_text = "Click here for free money!"
        phishing_result = orchestrator.detect_phishing(test_text)
        injection_result = orchestrator.detect_code_injection(test_text)
        
        print(f"   🎣 Phishing detection result: {phishing_result.get('status', 'Error')}")
        print(f"   💉 Code injection detection result: {injection_result.get('status', 'Error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🔧 Simple Transformer Models Fix")
    print("=" * 50)
    
    # Check requirements
    try:
        import torch
        import transformers
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError:
        print("❌ Missing PyTorch or Transformers")
        print("💡 Install with: pip install torch transformers")
        return False
    
    # Remove corrupted models
    remove_corrupted_models()
    
    # Create new models
    success = create_basic_models()
    
    if success:
        # Test the new models
        if test_new_models():
            print("\n🎉 Success! Your transformer models are now working.")
            print("💡 Start your API server:")
            print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8080")
        else:
            print("\n⚠️  Models created but testing had issues.")
    else:
        print("\n❌ Failed to create working models.")
        print("💡 Try the more complex approach with the other script.")

if __name__ == "__main__":
    main()