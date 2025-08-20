# api/orchestrator.py
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import joblib 
import os

class CybersecurityOrchestrator:
    def __init__(self):
        print("Loading models into memory...")

        # --- Load Network Models ---
        try:
            # Load Network Anomaly Detector (Isolation Forest)
            self.anomaly_model = joblib.load('../saved_models/isolation_forest_model.pkl')
            print("✅ Network Anomaly Detector loaded.")
        except Exception as e:
            print(f"⚠️ Failed to load Network Anomaly Detector: {e}")
            self.anomaly_model = None

        try:
            # Load Intrusion Detection System 
            self.intrusion_model = joblib.load('../saved_models/intrusion_detection_model.pkl')
            print("✅ Intrusion Detection System loaded.")
        except Exception as e:
            print(f"⚠️ Failed to load Intrusion Detection System: {e}")
            self.intrusion_model = None

        try:
            # Load scalers if you used them during training
            self.scaler = joblib.load('../saved_models/feature_scaler.pkl')
            print("✅ Feature Scaler loaded.")
        except Exception as e:
            print(f"⚠️ Failed to load Feature Scaler: {e}")
            self.scaler = None

        # --- Load Dynamic Behavior Analyzer ---
        try:
            self.dynamic_model = load_model('../saved_models/dynamic_behavior_analyzer.h5')
            self.sequence_length = 100 # Must be the same as used in training
            print("✅ Dynamic Behavior Analyzer loaded.")
        except Exception as e:
            print(f"⚠️ Failed to load Dynamic Behavior Analyzer: {e}")
            self.dynamic_model = None

    def predict_network_anomaly(self, features):
        """
        Predicts if network traffic is anomalous using Isolation Forest.
        :param features: A list of numerical features representing network traffic
        :return: Dictionary with prediction result
        """
        if self.anomaly_model is None:
            return {"error": "Network Anomaly Detector not available"}
        
        try:
            # Convert to numpy array and reshape for single prediction
            feature_array = np.array(features).reshape(1, -1)
            
            # Scale features if scaler is available
            if self.scaler is not None:
                feature_array = self.scaler.transform(feature_array)
            
            # Make prediction (-1 for anomaly, 1 for normal)
            prediction = self.anomaly_model.predict(feature_array)[0]
            
            # Get anomaly score (lower scores indicate more anomalous)
            anomaly_score = self.anomaly_model.decision_function(feature_array)[0]
            
            if prediction == -1:
                return {
                    "status": "Anomaly Detected",
                    "prediction": "Anomalous",
                    "anomaly_score": float(anomaly_score),
                    "confidence": abs(float(anomaly_score))
                }
            else:
                return {
                    "status": "Normal Traffic",
                    "prediction": "Normal",
                    "anomaly_score": float(anomaly_score),
                    "confidence": float(anomaly_score)
                }
                
        except Exception as e:
            return {"error": f"Error in anomaly prediction: {str(e)}"}

    def classify_network_intrusion(self, features):
        """
        Classifies the type of network intrusion.
        :param features: A list of numerical features representing network traffic
        :return: Dictionary with classification result
        """
        if self.intrusion_model is None:
            return {"error": "Intrusion Detection System not available"}
        
        try:
            # Convert to numpy array and reshape for single prediction
            feature_array = np.array(features).reshape(1, -1)
            
            # Scale features if scaler is available
            if self.scaler is not None:
                feature_array = self.scaler.transform(feature_array)
            
            # Make prediction
            prediction = self.intrusion_model.predict(feature_array)[0]
            
            # Get prediction probabilities if available
            if hasattr(self.intrusion_model, 'predict_proba'):
                probabilities = self.intrusion_model.predict_proba(feature_array)[0]
                max_prob = float(np.max(probabilities))
            else:
                max_prob = None
            
            # Define attack type mapping (adjust based on your training labels)
            attack_types = {
                0: "Normal",
                1: "DoS Attack", 
                2: "Probe Attack",
                3: "R2L Attack",
                4: "U2R Attack"
            }
            
            attack_type = attack_types.get(prediction, "Unknown")
            
            result = {
                "prediction": attack_type,
                "prediction_code": int(prediction),
                "status": "Attack Detected" if prediction != 0 else "Normal Traffic"
            }
            
            if max_prob is not None:
                result["confidence"] = max_prob
                
            return result
            
        except Exception as e:
            return {"error": f"Error in intrusion classification: {str(e)}"}

    def analyze_system_calls(self, call_sequence):
        """
        Analyzes a sequence of system calls to detect threats.
        :param call_sequence: A list of integers representing system calls. e.g., [10, 45, 192, ...]
        """
        if self.dynamic_model is None:
            return {"error": "Dynamic Behavior Analyzer not available"}
            
        try:
            # 1. Pad the new sequence to the required length
            padded_sequence = pad_sequences([call_sequence], maxlen=self.sequence_length, padding='post', truncating='post')

            # 2. Make a prediction
            prediction_prob = self.dynamic_model.predict(padded_sequence)[0][0]

            # 3. Interpret the result
            if prediction_prob > 0.5:
                return {
                    "status": "Attack",
                    "confidence": float(prediction_prob),
                    "prediction": "Malicious Behavior Detected"
                }
            else:
                return {
                    "status": "Normal",
                    "confidence": 1.0 - float(prediction_prob),
                    "prediction": "Normal Behavior"
                }
        except Exception as e:
            return {"error": f"Error in system call analysis: {str(e)}"}