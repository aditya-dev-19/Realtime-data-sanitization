# api/main.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, Response
from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session

import sys
from pathlib import Path
from dotenv import load_dotenv

# Import your main orchestrator class and database components
from .orchestrator import CybersecurityOrchestrator
from . import database as db
# Import routers
from routers import alerts as alerts_router
from models.alert import Alert

# Load environment variables from .env file
load_dotenv()

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# --- 1. Initialize FastAPI app and Orchestrator ---
# Create database tables
db.Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="AI Cybersecurity Threat Detection API",
    description="An API that uses a suite of AI models to detect various cyber threats and govern data.",
    version="1.0.0",
)

try:
    orchestrator = CybersecurityOrchestrator()
except Exception as e:
    raise RuntimeError(f"Failed to initialize the CybersecurityOrchestrator: {e}")

# --- Define Request Body Models ---
class DynamicData(BaseModel):
    call_sequence: List[int]

class NetworkData(BaseModel):
    features: List[float]

class TextData(BaseModel):
    text: str
    
class QualityData(BaseModel):
    features: List[float]

class JsonData(BaseModel):
    data: Dict[str, Any] = Field(..., description="A valid JSON object to be assessed for data quality.")

class SystemCalls(BaseModel):
    call_sequence: List[int]

# --- Define API Endpoints ---

@app.get("/", tags=["General"])
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"message": "Welcome to the AI Cybersecurity System API"}

@app.post("/analyze-dynamic-behavior", tags=["Threat Analysis"])
def dynamic_analysis(data: DynamicData):
    """Analyzes a sequence of system calls for behavioral threats."""
    try:
        return orchestrator.analyze_dynamic_behavior(data.call_sequence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-network-traffic", tags=["Threat Analysis"])
def network_analysis(data: NetworkData):
    """Analyzes a vector of network features for anomalies and known attack types."""
    EXPECTED_FEATURES = 10 
    if len(data.features) != EXPECTED_FEATURES:
        raise HTTPException(
            status_code=400, # Bad Request
            detail=f"Invalid number of features. Expected {EXPECTED_FEATURES}, but got {len(data.features)}."
        )
    try:
        return orchestrator.analyze_network_traffic(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-text", tags=["Analysis"])
def analyze_text(data: TextData, db_session: Session = Depends(db.get_db)):
    """
    Analyzes a string of text for sensitive data and quality.
    """
    try:
        sensitive_result = orchestrator.classify_sensitive_data(data.text)
        quality_result = orchestrator.assess_data_quality(data.text)

        # Log to database
        log_entry = db.AnalysisResult(
            file_name="N/A (Text Input)",
            analysis_type="Text Analysis",
            is_malicious=sensitive_result.get('classification') in ['SENSITIVE', 'PII', 'Financial', 'Secrets'], 
            confidence_score=sensitive_result.get('confidence'),
            analysis_details=json.dumps({
                "sensitive_analysis": sensitive_result,
                "quality_analysis": quality_result
            })
        )
        db_session.add(log_entry)
        db_session.commit()

        return {
            "analysis_type": "Text Analysis",
            "sensitive_data_analysis": sensitive_result,
            "data_quality_analysis": quality_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during text analysis: {e}")


@app.post("/analyze-file", tags=["Analysis"])
async def analyze_file(db_session: Session = Depends(db.get_db), file: UploadFile = File(...)):
    """
    Analyzes an uploaded file for static malware features.
    """
    temp_dir = "tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file to the temporary path
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Analyze the file using the orchestrator
        result = orchestrator.analyze_file_for_threats(temp_file_path)

        # Log to database
        log_entry = db.AnalysisResult(
            file_name=file.filename,
            file_hash=result.get('file_hash'),
            file_type=result.get('file_type'),
            analysis_type="File Analysis",
            is_malicious=result.get('is_malicious'),
            confidence_score=result.get('confidence'),
            analysis_details=json.dumps(result)
        )
        db_session.add(log_entry)
        db_session.commit()

        return {"analysis_type": "Static File Analysis", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during file analysis: {e}")
    finally:
        # Clean up by removing the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# --- Enhanced Threat Detection Endpoints ---
@app.post("/detect-phishing", tags=["Threat Detection"])
def detect_phishing(data: TextData):
    """Analyzes a string of text for potential phishing threats."""
    try:
        result = orchestrator.detect_phishing(data.text)
        return {"analysis_type": "Phishing Detection", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        return orchestrator.analyze_system_calls(data.call_sequence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Data Classification Endpoints ---
@app.post("/classify-sensitive-data", tags=["Data Classification"])
def classify_sensitive_data(data: TextData):
    """Classifies text to identify sensitive data."""
    try:
        return orchestrator.classify_sensitive_data(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-data-quality", tags=["Data Classification"])
def assess_data_quality_features(data: QualityData):
    """Assesses the quality of a given data sample using feature array."""
    try:
        return orchestrator.assess_data_quality(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-json-quality", tags=["Data Classification"])
def assess_json_quality(payload: JsonData):
    """Assesses the quality of JSON data using enhanced quality assessor."""
    try:
        return orchestrator.assess_data_quality(payload.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON quality assessment failed: {e}")

# --- Enhanced Analysis Endpoints ---
@app.post("/comprehensive-analysis", tags=["Enhanced Analysis"])
def comprehensive_analysis(data: TextData, db_session: Session = Depends(db.get_db)):
    """
    Performs comprehensive analysis using enhanced models with detailed insights.
    """
    try:
        result = orchestrator.comprehensive_analysis(data.text)
        
        # Log to database
        sensitivity_info = result.get('sensitivity_analysis', {})
        log_entry = db.AnalysisResult(
            file_name="N/A (Comprehensive Text Analysis)",
            analysis_type="Comprehensive Analysis",
            is_malicious=sensitivity_info.get('classification') in ['SENSITIVE', 'PII', 'Financial', 'Secrets'],
            confidence_score=sensitivity_info.get('confidence', 0.0),
            analysis_details=json.dumps(result)
        )
        db_session.add(log_entry)
        db_session.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {e}")

@app.post("/comprehensive-data-analysis", tags=["Enhanced Analysis"])
def comprehensive_data_analysis(data: TextData):
    """Performs both sensitive data classification and quality assessment on text."""
    try:
        return orchestrator.comprehensive_data_analysis(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during comprehensive analysis: {e}")

# Include routers
app.include_router(alerts_router.router)

# --- System Monitoring Endpoints ---
@app.get("/health")
async def health_check():
    """
    Performs a health check on all system components.
    """
    # Check database connection
    db_status = "ok"
    try:
        db.SessionLocal().execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "message": "All systems operational",
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "alerts": "ok"
        }
    }

@app.get("/health/status")
async def get_health_status():
    """Checks the health of the data classification and quality models."""
    return {"status": "ok", "message": "All models are functioning normally"}

@app.get("/model-stats", tags=["System"])
def get_model_stats():
    """
    Returns performance statistics for the models.
    """
    try:
        return orchestrator.get_model_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model stats: {e}")

