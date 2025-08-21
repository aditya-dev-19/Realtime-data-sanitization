# api/orchestrator.py
import os
# Force TensorFlow to use CPU to avoid CUDA errors on machines without a configured GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import sys
from pathlib import Path
import json

# Add project root to the Python path to allow for absolute imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import joblib 

# Import your custom model classes to resolve the unpickling error
from models.data_classification.sensitive_classifier import SensitiveDataClassifier
from models.data_classification.quality_assessor import DataQualityAssessor


class CybersecurityOrchestrator:
    def __init__(self, model_dir='../saved_models/'):
        print("Initializing Cybersecurity Orchestrator...")
        
        # 1. Load Dynamic Behavior Analyzer (LSTM)
        try:
            self.dynamic_model = load_model(f'{model_dir}dynamic_behavior_analyzer.h5')
            with open(f'{model_dir}model_metadata.json', 'r') as f:
                self.dynamic_metadata = json.load(f)
            self.sequence_length = self.dynamic_metadata['sequence_length']
            print("✅ Dynamic Behavior Analyzer loaded.")
        except Exception as e:
            print(f"❌ ERROR loading Dynamic Behavior Analyzer: {e}")

        # 2. Load Network Traffic Models
        try:
            self.iso_forest = joblib.load(f'{model_dir}isolation_forest_model.pkl')
            self.ids_model = joblib.load(f'{model_dir}intrusion_detection_model.pkl')
            self.network_scaler = joblib.load(f'{model_dir}feature_scaler.pkl')
            print("✅ Network Traffic models loaded.")
        except Exception as e:
            print(f"❌ ERROR loading Network Traffic models: {e}")

        # 3. Load Data Classification Models
        try:
            self.sensitive_classifier = joblib.load(f'{model_dir}classifier.pkl')
            self.quality_assessor = joblib.load(f'{model_dir}assessor.pkl')
            # Assuming metadata.json is for the sensitive classifier
            with open(f'{model_dir}metadata.json', 'r') as f:
                self.sensitive_metadata = json.load(f)
            print("✅ Data Classification models loaded.")
        except Exception as e:
            print(f"❌ ERROR loading Data Classification models: {e}")

        print("\n🚀 Orchestrator ready!")

    def analyze_dynamic_behavior(self, call_sequence: list[int]):
        """Analyzes a sequence of system calls with the LSTM model."""
        padded_sequence = pad_sequences([call_sequence], maxlen=self.sequence_length, padding='post', truncating='post')
        prediction_prob = self.dynamic_model.predict(padded_sequence)[0][0]
        
        if prediction_prob > 0.5:
            return {"status": "Attack Behavior Detected", "confidence": float(prediction_prob)}
        else:
            return {"status": "Normal Behavior", "confidence": 1.0 - float(prediction_prob)}

    def analyze_network_traffic(self, features: list[float]):
        """Analyzes network features with both anomaly and intrusion detection models."""
        features_2d = np.array(features).reshape(1, -1)
        scaled_features = self.network_scaler.transform(features_2d)
        
        # Anomaly Detection
        anomaly_prediction = self.iso_forest.predict(scaled_features)
        anomaly_status = "Anomaly" if anomaly_prediction[0] == -1 else "Normal"
        
        # Intrusion Classification
        intrusion_prediction = self.ids_model.predict(scaled_features)
        
        return {
            "anomaly_detection": {"status": anomaly_status},
            "intrusion_classification": {"attack_type": intrusion_prediction[0]}
        }

    def classify_sensitive_data(self, text: str):
        """Classifies text to identify sensitive data."""
        prediction = self.sensitive_classifier.predict([text])
        # Assuming the model returns a label directly
        return {"data_type": prediction[0], "details": "Model classified text content."}

    def assess_data_quality(self, features: list[float]):
        """Assesses the quality of a given data sample."""
        features_2d = np.array(features).reshape(1, -1)
        quality_score = self.quality_assessor.predict(features_2d)
        
        return {"quality_score": quality_score[0], "recommendation": "Review data if score is low."}