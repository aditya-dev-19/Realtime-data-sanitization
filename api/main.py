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

try:
    orchestrator = CybersecurityOrchestrator()
except Exception as e:
    # If models fail to load, we can't start the app.
    raise RuntimeError(f"Failed to initialize the CybersecurityOrchestrator: {e}")

# --- 2. Define Request Body Models (using Pydantic) ---
# This ensures that incoming data has the correct structure.

class TextData(BaseModel):
    text: str

class NetworkFeatures(BaseModel):
    features: List[float]

class SystemCalls(BaseModel):
    calls: List[int]


# --- 3. Define API Endpoints ---

@app.get("/", tags=["General"])
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"message": "Welcome to the AI Cybersecurity System API"}

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