# api/orchestrator.py
import os
from pathlib import Path
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import joblib 

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Assuming api_interface is in models/data_classification
from models.data_classification.api_interface import DataClassificationAPI

class CybersecurityOrchestrator:
    def __init__(self):
        print("Loading models into memory...")

        # --- CORRECTED: Build absolute paths that match your folder structure ---
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Construct paths using the exact folder names from your screenshot
        phishing_model_path = project_root / "saved_models" / "phishing_model_v2"
        code_injection_model_path = project_root / "saved_models" / "code_injection_model_prod"
        dynamic_model_path = project_root / "saved_models" / "dynamic_behavior_analyzer.h5"
        # --- END CORRECTION ---

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Using device: {self.device}")

        try:
            self.phishing_tokenizer = AutoTokenizer.from_pretrained(phishing_model_path)
            self.phishing_model = AutoModelForSequenceClassification.from_pretrained(phishing_model_path)
            self.phishing_model.to(self.device)
            print("✅ Phishing Detection Model loaded.")

            self.code_injection_tokenizer = AutoTokenizer.from_pretrained(code_injection_model_path)
            self.code_injection_model = AutoModelForSequenceClassification.from_pretrained(code_injection_model_path)
            self.code_injection_model.to(self.device)
            print("✅ Code Injection Detection Model loaded.")

        except Exception as e:
            print(f"❌ CRITICAL: Failed to load Transformer models: {e}")
            raise e

        self.dynamic_model = load_model(dynamic_model_path)
        self.sequence_length = 100
        print("✅ Dynamic Behavior Analyzer loaded.")

        try:
            self.data_classification_service = DataClassificationAPI()
            print("✅ Data Classification and Quality models loaded successfully.")
        except Exception as e:
            print(f"❌ CRITICAL: Failed to load Data Classification models: {e}")
            raise e

    def detect_phishing(self, text: str):
        """Analyzes text to detect phishing attempts using a transformer model."""
        inputs = self.phishing_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.phishing_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0, prediction].item()
        label = self.phishing_model.config.id2label[prediction]
        return {"status": label, "confidence": confidence}

    def detect_code_injection(self, text: str):
        """Analyzes text to detect code injection attempts using a transformer model."""
        inputs = self.code_injection_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.code_injection_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0, prediction].item()
        label = self.code_injection_model.config.id2label[prediction]
        return {"status": label, "confidence": confidence}

    def analyze_system_calls(self, call_sequence):
        padded_sequence = pad_sequences([call_sequence], maxlen=self.sequence_length, padding='post', truncating='post')
        prediction_prob = self.dynamic_model.predict(padded_sequence)[0][0]
        if prediction_prob > 0.5:
            return {"status": "Attack", "confidence": float(prediction_prob)}
        else:
            return {"status": "Normal", "confidence": 1.0 - float(prediction_prob)}
    
    def classify_sensitive_data(self, text: str):
        return self.data_classification_service.classify(text)

    def assess_data_quality(self, data: dict):
        return self.data_classification_service.assess_data_quality(data)

    def comprehensive_data_analysis(self, text: str):
        return self.data_classification_service.comprehensive_analysis(text)

    def get_data_services_health(self):
        return self.data_classification_service.health_check()