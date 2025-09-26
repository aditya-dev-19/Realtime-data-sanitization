#!/usr/bin/env python3
"""
Quick test to check if the phishing and code injection models can be loaded manually.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    print("✅ Transformers library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import transformers: {e}")
    sys.exit(1)

# Test phishing model
phishing_path = backend_dir / "downloaded_models" / "phishing_model_v2"
print(f"Checking phishing model at: {phishing_path}")

if phishing_path.exists():
    try:
        print("Loading phishing tokenizer...")
        phishing_tokenizer = AutoTokenizer.from_pretrained(phishing_path)
        print("✅ Phishing tokenizer loaded successfully")

        print("Loading phishing model...")
        phishing_model = AutoModelForSequenceClassification.from_pretrained(phishing_path)
        print("✅ Phishing model loaded successfully")

        # Test with sample phishing text
        test_text = "URGENT: Click here to verify your account: http://phishing-site.com/verify"

        print(f"Testing with text: {test_text}")
        inputs = phishing_tokenizer(test_text, return_tensors="pt", truncation=True, padding=True, max_length=512)

        print("Running inference...")
        with torch.no_grad():
            outputs = phishing_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1).item()

        confidence = probabilities[0, prediction].item()
        label = phishing_model.config.id2label[prediction]

        print(f"Prediction: {label}")
        print(f"Confidence: {confidence:.4f}")
        print(f"Probabilities: {probabilities}")

    except Exception as e:
        print(f"❌ Error loading/testing phishing model: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Phishing model directory not found: {phishing_path}")

print("\n" + "="*50)

# Test code injection model
code_injection_path = backend_dir / "downloaded_models" / "code_injection_model_prod"
print(f"Checking code injection model at: {code_injection_path}")

if code_injection_path.exists():
    try:
        print("Loading code injection tokenizer...")
        code_injection_tokenizer = AutoTokenizer.from_pretrained(code_injection_path)
        print("✅ Code injection tokenizer loaded successfully")

        print("Loading code injection model...")
        code_injection_model = AutoModelForSequenceClassification.from_pretrained(code_injection_path)
        print("✅ Code injection model loaded successfully")

        # Test with sample XSS text
        test_text = "<script>alert('XSS')</script>"

        print(f"Testing with text: {test_text}")
        inputs = code_injection_tokenizer(test_text, return_tensors="pt", truncation=True, padding=True, max_length=512)

        print("Running inference...")
        with torch.no_grad():
            outputs = code_injection_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1).item()

        confidence = probabilities[0, prediction].item()
        label = code_injection_model.config.id2label[prediction]

        print(f"Prediction: {label}")
        print(f"Confidence: {confidence:.4f}")
        print(f"Probabilities: {probabilities}")

    except Exception as e:
        print(f"❌ Error loading/testing code injection model: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Code injection model directory not found: {code_injection_path}")

print("\n" + "="*50)
print("Model loading test completed!")
