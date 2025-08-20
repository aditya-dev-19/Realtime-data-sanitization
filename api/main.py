import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

# Import your main orchestrator class
from orchestrator import CybersecurityOrchestrator

# --- 1. Initialize FastAPI app and Orchestrator ---
app = FastAPI(
    title="AI Cybersecurity Threat Detection API",
    description="An API that uses a suite of AI models to detect various cyber threats.",
    version="1.0.0",
)

# Initialize orchestrator with better error handling
orchestrator = None
try:
    orchestrator = CybersecurityOrchestrator()
    print("✅ CybersecurityOrchestrator initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Some models failed to load: {e}")
    # Still create the orchestrator, individual methods will handle missing models
    orchestrator = CybersecurityOrchestrator()

# --- 2. Define Request Body Models (using Pydantic) ---
class TextData(BaseModel):
    text: str

class NetworkFeatures(BaseModel):
    features: List[float]
    
    class Config:
        # Example of expected input
        schema_extra = {
            "example": {
                "features": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            }
        }

class SystemCalls(BaseModel):
    calls: List[int]
    
    class Config:
        schema_extra = {
            "example": {
                "calls": [1, 5, 10, 15, 20, 25, 30, 35, 40, 45]
            }
        }

# --- 3. Define API Endpoints ---

@app.get("/", tags=["General"])
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"message": "Welcome to the AI Cybersecurity System API"}

@app.get("/health", tags=["General"])
def health_check():
    """Check the health status of all loaded models."""
    status = {
        "api_status": "running",
        "models": {
            "dynamic_behavior_analyzer": orchestrator.dynamic_model is not None,
            "network_anomaly_detector": orchestrator.anomaly_model is not None,
            "intrusion_detection_system": orchestrator.intrusion_model is not None,
            "feature_scaler": orchestrator.scaler is not None
        }
    }
    return status

@app.post("/analyze-text", tags=["Analysis"])
def analyze_text(data: TextData):
    """Analyzes a string of text for potential threats (e.g., phishing)."""
    # NOTE: You will need to implement the 'analyze_text_threat' method in your orchestrator
    # result = orchestrator.analyze_text_threat(data.text)
    # return {"analysis_type": "Text Threat", "result": result}
    return {"analysis_type": "Text Threat", "status": "Endpoint not fully implemented yet."}

@app.post("/analyze-file", tags=["Analysis"])
async def analyze_file(file: UploadFile = File(...)):
    """Analyzes an uploaded file for static malware features."""
    # Create a temporary directory to store uploaded files
    temp_dir = "tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file to the temporary path
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # NOTE: You will need to implement the 'analyze_file_threat' method in your orchestrator
        # This method should take a file path as input
        # result = orchestrator.analyze_file_threat(temp_file_path)
        result = {"filename": file.filename, "status": "Endpoint not fully implemented yet."}
        return {"analysis_type": "Static File Analysis", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during file analysis: {e}")
    finally:
        # Clean up by removing the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/analyze-network-traffic", tags=["Analysis"])
def analyze_network_traffic(data: NetworkFeatures):
    """Analyzes a vector of network features for anomalies and known attack types."""
    try:
        anomaly_result = orchestrator.predict_network_anomaly(data.features)
        intrusion_result = orchestrator.classify_network_intrusion(data.features)
        
        return {
            "analysis_type": "Network Traffic",
            "anomaly_detection": anomaly_result,
            "intrusion_classification": intrusion_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during network analysis: {e}")

@app.post("/analyze-system-calls", tags=["Analysis"])
def analyze_system_calls(data: SystemCalls):
    """Analyzes a sequence of system calls for behavioral threats."""
    try:
        result = orchestrator.analyze_system_calls(data.calls)
        return {"analysis_type": "Dynamic Behavior Analysis", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during system call analysis: {e}")

# --- 4. Additional utility endpoints ---

@app.post("/batch-analyze-network", tags=["Analysis"])
def batch_analyze_network(data: List[NetworkFeatures]):
    """Analyzes multiple network traffic samples at once."""
    results = []
    for i, sample in enumerate(data):
        try:
            anomaly_result = orchestrator.predict_network_anomaly(sample.features)
            intrusion_result = orchestrator.classify_network_intrusion(sample.features)
            results.append({
                "sample_id": i,
                "anomaly_detection": anomaly_result,
                "intrusion_classification": intrusion_result
            })
        except Exception as e:
            results.append({
                "sample_id": i,
                "error": str(e)
            })
    
    return {
        "analysis_type": "Batch Network Traffic Analysis",
        "total_samples": len(data),
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)