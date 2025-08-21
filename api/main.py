# api/main.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import json
from sqlalchemy.orm import Session

# Import your main orchestrator class and database components
from orchestrator import CybersecurityOrchestrator
import database as db

# --- 1. Initialize FastAPI app and Orchestrator ---
# Create database tables
db.Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="AI Cybersecurity Threat Detection API",
    description="An API that uses a suite of AI models to detect various cyber threats.",
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
    try:
        return orchestrator.analyze_network_traffic(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify-sensitive-data", tags=["Data Classification"])
def sensitive_data_analysis(data: TextData):
    """Classifies text to identify sensitive data."""
    try:
        return orchestrator.classify_sensitive_data(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-data-quality", tags=["Data Classification"])
def data_quality_analysis(data: QualityData):
    """Assesses the quality of a given data sample."""
    try:
        return orchestrator.assess_data_quality(data.features)
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
            is_malicious=sensitive_result.get('is_sensitive', False), # Treat sensitive as "malicious" for this context
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