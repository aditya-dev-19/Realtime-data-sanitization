#!/usr/bin/env python3
"""
Simple test to check if the models are working correctly.
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

# Test phishing model only first
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

        # Test with obvious phishing text
        phishing_text = "URGENT: Your account has been compromised! Click here immediately to verify: http://secure-bank-login.com/verify Account Number: 1234-5678-9012-3456 If you don't act now, your account will be suspended!"

        print(f"Testing with phishing text: {phishing_text[:100]}...")
        inputs = phishing_tokenizer(phishing_text, return_tensors="pt", truncation=True, padding=True, max_length=512)

        print("Running inference...")
        with torch.no_grad():
            outputs = phishing_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1).item()

        confidence = probabilities[0, prediction].item()
        label = phishing_model.config.id2label[prediction]

        print(f"✅ Phishing Model Results:")
        print(f"   Prediction: {label}")
        print(f"   Confidence: {confidence:.4f}")
        print(f"   Probabilities: {probabilities[0].tolist()}")

        if label == "Phishing" and confidence > 0.5:
            print("✅ Phishing model is working correctly!")
        else:
            print(f"❌ Phishing model returned unexpected result: {label} with confidence {confidence:.4f}")

    except Exception as e:
        print(f"❌ Error loading/testing phishing model: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Phishing model directory not found: {phishing_path}")

print("\n" + "="*50)
print("Simple model test completed!")
