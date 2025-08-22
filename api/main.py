# api/main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from .orchestrator import CybersecurityOrchestrator

# --- 1. Initialize FastAPI app and Orchestrator ---
app = FastAPI(
    title="AI Cybersecurity Threat Detection API",
    description="An API that uses a suite of AI models to detect various cyber threats and govern data.",
    version="1.0.0",
)

try:
    orchestrator = CybersecurityOrchestrator()
except Exception as e:
    raise RuntimeError(f"Failed to initialize the CybersecurityOrchestrator: {e}")

# --- 2. Define Request Body Models ---
class TextData(BaseModel):
    text: str

class NetworkFeatures(BaseModel):
    features: List[float]

class SystemCalls(BaseModel):
    calls: List[int]

class JsonData(BaseModel):
    data: Dict[str, Any] = Field(..., description="A valid JSON object to be assessed for data quality.")

# --- 3. Define API Endpoints ---

@app.get("/", tags=["General"])
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"message": "Welcome to the AI Cybersecurity System API"}

# --- MODIFIED: This endpoint now detects phishing ---
@app.post("/detect-phishing", tags=["Threat Detection"])
def detect_phishing(data: TextData):
    """Analyzes a string of text for potential phishing threats."""
    try:
        result = orchestrator.detect_phishing(data.text)
        return {"analysis_type": "Phishing Detection", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: This endpoint detects code injection ---
@app.post("/detect-code-injection", tags=["Threat Detection"])
def detect_code_injection(data: TextData):
    """Analyzes a string of text (e.g., code snippet) for injection threats."""
    try:
        result = orchestrator.detect_code_injection(data.text)
        return {"analysis_type": "Code Injection Detection", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-system-calls", tags=["Threat Detection"])
def analyze_system_calls(data: SystemCalls):
    """Analyzes a sequence of system calls for behavioral threats."""
    try:
        result = orchestrator.analyze_system_calls(data.calls)
        return {"analysis_type": "Dynamic Behavior Analysis", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during system call analysis: {e}")

# --- Data Governance Endpoints ---
@app.get("/health-data-services", tags=["Data Governance"])
def get_health_status():
    """Checks the health of the data classification and quality models."""
    try:
        return orchestrator.get_data_services_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during health check: {e}")

@app.post("/classify-sensitive-data", tags=["Data Governance"])
def classify_sensitive_data(data: TextData):
    """Classifies a string of text for sensitive data (PII, Financial, etc.)."""
    try:
        return orchestrator.classify_sensitive_data(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during text classification: {e}")

@app.post("/assess-data-quality", tags=["Data Governance"])
def assess_data_quality(payload: JsonData):
    """Assesses the completeness and quality of a given JSON dataset."""
    try:
        return orchestrator.assess_data_quality(payload.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during data quality assessment: {e}")

@app.post("/comprehensive-data-analysis", tags=["Data Governance"])
def comprehensive_data_analysis(data: TextData):
    """Performs both sensitive data classification and quality assessment on text."""
    try:
        return orchestrator.comprehensive_data_analysis(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during comprehensive analysis: {e}")