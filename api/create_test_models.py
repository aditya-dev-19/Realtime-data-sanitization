# create_test_dynamic_model.py
# Run this script to create a compatible test model
import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Create saved_models directory if it doesn't exist
os.makedirs('../saved_models', exist_ok=True)

# 1. Create a simple Dynamic Behavior Analyzer (LSTM model)
print("Creating Dynamic Behavior Analyzer...")
model = Sequential([
    Embedding(input_dim=1000, output_dim=64, input_length=100),  # For system calls
    LSTM(128, return_sequences=True),
    LSTM(64),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Binary classification: 0=Normal, 1=Attack
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Save the model
model.save('../saved_models/dynamic_behavior_analyzer.h5')
print("✅ Dynamic Behavior Analyzer created and saved!")

# 2. Create a simple Network Anomaly Detector (Isolation Forest)
print("Creating Network Anomaly Detector...")
# Create with some default parameters
anomaly_detector = IsolationForest(
    contamination=0.1,  # Expected proportion of outliers
    random_state=42,
    n_estimators=100
)

# Fit on dummy data (you should replace this with real training data)
dummy_data = np.random.randn(1000, 10)  # 1000 samples, 10 features
anomaly_detector.fit(dummy_data)

# Save the model
joblib.dump(anomaly_detector, '../saved_models/isolation_forest_model.pkl')
print("✅ Network Anomaly Detector created and saved!")

# 3. Create a simple Intrusion Detection System (Random Forest)
print("Creating Intrusion Detection System...")
from sklearn.ensemble import RandomForestClassifier

intrusion_detector = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Fit on dummy data (5 classes: Normal, DoS, Probe, R2L, U2R)
dummy_features = np.random.randn(1000, 10)
dummy_labels = np.random.randint(0, 5, 1000)
intrusion_detector.fit(dummy_features, dummy_labels)

# Save the model
joblib.dump(intrusion_detector, '../saved_models/intrusion_detection_model.pkl')
print("✅ Intrusion Detection System created and saved!")

# 4. Create a Feature Scaler
print("Creating Feature Scaler...")
scaler = StandardScaler()
scaler.fit(dummy_data)

# Save the scaler
joblib.dump(scaler, '../saved_models/feature_scaler.pkl')
print("✅ Feature Scaler created and saved!")

print("\n🎉 All test models created successfully!")
print("Now restart your API server to load the new models.")