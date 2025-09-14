# deploy_api.py

from fastapi import FastAPI
from pydantic import BaseModel
from models.network_analyzer import NetworkAnomalyDetector, IntrusionDetectionSystem
# Import necessary libraries
import joblib
import pandas as pd
import numpy as np
import json
import logging
from sklearn.preprocessing import LabelEncoder # Ensure LabelEncoder is available for preprocessing
import os
import sys
from pathlib import Path


# Setup logging (if not already configured)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Define model paths (assuming they are accessible locally)
# Update these paths if your models are saved elsewhere
SCRIPT_DIR = Path(__file__).parent.absolute()
BASE_DIR = SCRIPT_DIR

# Define model paths
SAVED_MODELS_DIR = BASE_DIR / 'saved_models'
ANOMALY_DETECTOR_PATH = SAVED_MODELS_DIR / 'network_anomaly_detector.pkl'
INTRUSION_DETECTOR_PATH = SAVED_MODELS_DIR / 'network_intrusion_detector.pkl'
MODEL_METADATA_PATH = SAVED_MODELS_DIR / 'model_metadata.json'


# Load the trained models
anomaly_detector = None
intrusion_detector = None
model_metadata = None

try:
    logging.info(f"Loading Anomaly Detector from {ANOMALY_DETECTOR_PATH}")
    anomaly_detector = joblib.load(ANOMALY_DETECTOR_PATH)
    logging.info("Anomaly Detector loaded successfully.")

    logging.info(f"Loading Intrusion Detector from {INTRUSION_DETECTOR_PATH}")
    intrusion_detector = joblib.load(INTRUSION_DETECTOR_PATH)
    logging.info("Intrusion Detector loaded successfully.")

    logging.info(f"Loading Model Metadata from {MODEL_METADATA_PATH}")
    with open(MODEL_METADATA_PATH, 'r') as f:
        model_metadata = json.load(f)
    logging.info("Model Metadata loaded successfully.")

except FileNotFoundError as e:
    logging.error(f"Model file not found: {e}")
    # In a real deployment, you might want to raise an exception or exit here
    # raise e
except Exception as e:
    logging.error(f"Error loading models: {e}")
    # In a real deployment, you might want to raise an exception or exit here
    # raise e


# Define the input data model based on expected features
# Refer to the features used during training (from model_metadata or training script)
# Example features - adjust based on your actual model's input
class NetworkTrafficData(BaseModel):
    duration: float
    protocol_type: str
    service: str
    flag: str
    src_bytes: float
    dst_bytes: float
    land: int
    wrong_fragment: float
    urgent: float
    hot: float
    num_failed_logins: float
    logged_in: int
    num_compromised: float
    root_shell: int
    su_attempted: int
    num_root: float
    num_file_creations: float
    num_shells: float
    num_access_files: float
    num_outbound_cmds: float
    is_host_login: int
    is_guest_login: int
    count: float
    srv_count: float
    serror_rate: float
    rerror_rate: float
    same_srv_rate: float
    diff_srv_rate: float
    srv_diff_host_rate: float
    dst_host_count: float
    dst_host_srv_count: float
    dst_host_same_srv_rate: float
    dst_host_diff_srv_rate: float
    dst_host_same_src_port_rate: float
    dst_host_srv_diff_host_rate: float
    dst_host_serror_rate: float
    dst_host_srv_serror_rate: float
    dst_host_rerror_rate: float
    dst_host_srv_rerror_rate: float
    # Add engineered features if your models expect them directly
    # total_bytes: float = None # Use default=None for optional/engineered features
    # bytes_ratio: float = None
    # conn_per_sec: float = None
    # srv_ratio: float = None
    # total_error_rate: float = None


# Instantiate the FastAPI application
app = FastAPI()

# Define the prediction endpoint
@app.post("/predict")
def predict_network_traffic(data: NetworkTrafficData):
    """
    Receives network traffic data and returns anomaly/intrusion predictions.
    """
    if anomaly_detector is None or intrusion_detector is None:
        logging.error("Models are not loaded.")
        return {"error": "Models not loaded. Please check server logs."}

    try:
        # Convert Pydantic object to pandas DataFrame
        # Ensure the column order matches the training data features
        input_data_dict = data.dict()
        # Ensure all expected features from training are present, add NaNs for missing ones
        # This is crucial if the input data schema is smaller than training features
        expected_features_ids = intrusion_detector.feature_names_ if hasattr(intrusion_detector, 'feature_names_') and intrusion_detector.feature_names_ is not None else list(input_data_dict.keys())
        expected_features_anomaly = anomaly_detector.feature_names if hasattr(anomaly_detector, 'feature_names') and anomaly_detector.feature_names is not None else list(input_data_dict.keys())

        # Combine all unique expected features
        all_expected_features = list(set(expected_features_ids + expected_features_anomaly))

        # Create DataFrame ensuring all expected columns are present
        input_df = pd.DataFrame([input_data_dict])
        input_df = input_df.reindex(columns=all_expected_features)


        # --- Preprocess data for Anomaly Detection ---
        # The preprocess_data method in NetworkAnomalyDetector handles scaling and categorical encoding
        # It expects the raw DataFrame and returns the scaled numpy array
        # We need to ensure the input_df has the correct columns the anomaly detector expects
        # The anomaly_detector.preprocess_data method handles selecting the correct columns internally
        X_anomaly_processed = anomaly_detector.preprocess_data(input_df.copy())


        # --- Preprocess data for Intrusion Detection ---
        # The preprocess_data method in IntrusionDetectionSystem handles scaling and categorical encoding
        # It expects the raw DataFrame and returns the scaled DataFrame
        # We need to ensure the input_df has the correct columns the intrusion detector expects
        # The intrusion_detector.preprocess_data method handles selecting and ordering columns internally
        X_intrusion_processed, _ = intrusion_detector.preprocess_data(input_df.copy(), target_col=None)


        # --- Perform Predictions ---
        # Anomaly Detection Prediction
        anomaly_results = anomaly_detector.predict(X_anomaly_processed)
        is_anomaly = bool(anomaly_results['ensemble']['predictions'][0]) # Convert numpy bool to Python bool
        anomaly_score_if = float(anomaly_results['isolation_forest']['scores'][0])
        anomaly_score_ae = float(anomaly_results['autoencoder']['scores'][0])


        # Intrusion Detection Prediction
        # The predict method in IntrusionDetectionSystem handles preprocessing and returns a dictionary
        intrusion_results = intrusion_detector.predict(input_df.copy())
        predicted_attack_label = str(intrusion_results['attack_labels'][0])
        prediction_confidence = float(intrusion_results['confidence'][0])


        # --- Prepare Response ---
        response = {
            "status": "success",
            "analysis": {
                "is_anomaly": is_anomaly,
                "anomaly_scores": {
                    "isolation_forest": anomaly_score_if,
                    "autoencoder": anomaly_score_ae
                },
                "predicted_attack_type": predicted_attack_label,
                "prediction_confidence": prediction_confidence
            }
        }

        logging.info(f"Prediction: Anomaly={is_anomaly}, Attack={predicted_attack_label} ({prediction_confidence:.3f})")

        return response

    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return {"status": "error", "message": str(e)}

# Removed the if __name__ == '__main__': block that runs uvicorn server
# This block is for running the script as a standalone application
# if __name__ == '__main__':
#     import uvicorn
#     logging.info("Starting FastAPI application...")
#     uvicorn.run(app, host="127.0.0.1", port=8000)