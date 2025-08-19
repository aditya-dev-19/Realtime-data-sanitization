# api/orchestrator.py
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
# --- Import other necessary libraries like joblib ---
import joblib 

class CybersecurityOrchestrator:
    def __init__(self):
        print("Loading models into memory...")

        # --- Example of loading other models ---
        # self.anomaly_model = joblib.load('../saved_models/isolation_forest_model.pkl')
        # print("✅ Network Anomaly Detector loaded.")

        # --- Load Dynamic Behavior Analyzer ---
        self.dynamic_model = load_model('../saved_models/dynamic_behavior_analyzer.h5')
        self.sequence_length = 100 # Must be the same as used in training
        print("✅ Dynamic Behavior Analyzer loaded.")

    def analyze_system_calls(self, call_sequence):
        """
        Analyzes a sequence of system calls to detect threats.
        :param call_sequence: A list of integers representing system calls. e.g., [10, 45, 192, ...]
        """
        # 1. Pad the new sequence to the required length
        padded_sequence = pad_sequences([call_sequence], maxlen=self.sequence_length, padding='post', truncating='post')

        # 2. Make a prediction
        prediction_prob = self.dynamic_model.predict(padded_sequence)[0][0]

        # 3. Interpret the result
        if prediction_prob > 0.5:
            return {
                "status": "Attack",
                "confidence": float(prediction_prob)
            }
        else:
            return {
                "status": "Normal",
                "confidence": 1.0 - float(prediction_prob)
            }
    
    # --- Add your other prediction methods here ---
    # def predict_network_anomaly(...)
    # def classify_network_intrusion(...)