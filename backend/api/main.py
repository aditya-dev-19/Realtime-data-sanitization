import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, Response
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from google.cloud import storage
from dotenv import load_dotenv


# --- Local Imports ---
# No longer imports 'database' or SQLAlchemy models that were deleted.
from .orchestrator import CybersecurityOrchestrator
from .storage_handler import encrypt_and_upload_file, download_and_decrypt_file_by_doc
from .routers import users, alerts
from .firebase_admin import db # Using Firestore for all database operations

# --- Global Orchestrator ---
# This will hold the loaded models so they are accessible to your endpoints.
orchestrator: CybersecurityOrchestrator = None

# Add the project's root directory to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Load environment variables from the .env file
load_dotenv(os.path.join(project_root, '.env'))

# --- GCS Model Download Function ---
def download_models_from_gcs(bucket_name: str, destination_folder: str = "downloaded_models"):
    """
    Downloads all files from a specified GCS bucket to a local folder.
    This function will be called once when the application starts.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            print(f"Created local directory for models: {destination_folder}")

        print(f"Starting model download from GCS bucket '{bucket_name}'...")
        for blob in blobs:
            destination_file_name = os.path.join(destination_folder, blob.name)
            # Ensure subdirectories exist locally before downloading
            os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
            
            blob.download_to_filename(destination_file_name)
            print(f"Successfully downloaded {blob.name} to {destination_file_name}")
        print("All models downloaded successfully.")

    except Exception as e:
        print(f"FATAL: An error occurred while downloading models: {e}")
        # This will prevent the server from starting if models can't be downloaded.
        raise


# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Cybersecurity Threat Detection API",
    description="An API that uses a suite of AI models to detect various cyber threats and govern data.",
    version="1.0.0",
)

# --- Application Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    This function runs ONCE when the FastAPI application starts.
    It handles downloading the ML models and initializing the orchestrator.
    """
    global orchestrator
    
    bucket_name = "realtime-data-sanitization-models"  # 👈 Your GCS bucket name
    local_models_folder = "downloaded_models"
    
    # Step 1: Download the models from GCS
    download_models_from_gcs(bucket_name, local_models_folder)
    
    # Step 2: Initialize the orchestrator with the path to the downloaded models
    print("Initializing Cybersecurity Orchestrator...")
    orchestrator = CybersecurityOrchestrator(model_dir=local_models_folder)
    print("Orchestrator initialized. Models are ready to serve requests.")


# --- Dependency Injection for the Orchestrator ---
def get_orchestrator():
    """
    Dependency function that provides the global orchestrator instance to API endpoints.
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator is not available or still initializing.")
    return orchestrator


# --- Pydantic Request Body Models ---
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

# --- API Endpoints ---

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Welcome to the AI Cybersecurity System API"}

@app.post("/analyze-dynamic-behavior", tags=["Threat Analysis"])
def dynamic_analysis(data: DynamicData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.analyze_dynamic_behavior(data.call_sequence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-network-traffic", tags=["Threat Analysis"])
def network_analysis(data: NetworkData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    EXPECTED_FEATURES = 10 
    if len(data.features) != EXPECTED_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid number of features. Expected {EXPECTED_FEATURES}, but got {len(data.features)}."
        )
    try:
        return orch.analyze_network_traffic(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [CORRECTED] Removed the db_session dependency from this endpoint
@app.post("/analyze-text", tags=["Analysis"])
def analyze_text(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    """
    Analyzes text. Logging to a database is now handled by the alerts router.
    """
    try:
        sensitive_result = orch.classify_sensitive_data(data.text)
        quality_result = orch.assess_data_quality(data.text)
        
        return {
            "analysis_type": "Text Analysis",
            "sensitive_data_analysis": sensitive_result,
            "data_quality_analysis": quality_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during text analysis: {e}")

# [CORRECTED] Removed the db_session dependency from this endpoint
@app.post("/analyze-file", tags=["Analysis"])
async def analyze_file(file: UploadFile = File(...), orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    temp_dir = "tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = orch.analyze_file_for_threats(temp_file_path)
        return {"analysis_type": "Static File Analysis", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during file analysis: {e}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/detect-phishing", tags=["Threat Detection"])
def detect_phishing(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.detect_phishing(data.text)
        return {"analysis_type": "Phishing Detection", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-code-injection", tags=["Threat Detection"])
def detect_code_injection(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.detect_code_injection(data.text)
        return {"analysis_type": "Code Injection Detection", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-system-calls", tags=["Threat Detection"])
def analyze_system_calls(data: SystemCalls, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.analyze_system_calls(data.call_sequence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify-sensitive-data", tags=["Data Classification"])
def classify_sensitive_data(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.classify_sensitive_data(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-data-quality", tags=["Data Classification"])
def assess_data_quality_features(data: QualityData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.assess_data_quality(data.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-json-quality", tags=["Data Classification"])
def assess_json_quality(payload: JsonData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.assess_data_quality(payload.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON quality assessment failed: {e}")

# [CORRECTED] Removed the db_session dependency from this endpoint
@app.post("/comprehensive-analysis", tags=["Enhanced Analysis"])
def comprehensive_analysis(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.comprehensive_analysis(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {e}")

@app.post("/comprehensive-data-analysis", tags=["Enhanced Analysis"])
def comprehensive_data_analysis(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.comprehensive_data_analysis(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during comprehensive analysis: {e}")
        
@app.get("/health", tags=["System Monitoring"])
async def health_check():
    # Check if using Firestore (which doesn't need a session)
    db_status = "ok"
    try:
        # Try a simple Firestore operation to verify connection
        db.collection('health_check').document('status').get()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "message": "All systems operational" if db_status == "ok" else "Some components are experiencing issues",
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "orchestrator_status": "loaded" if orchestrator else "not_loaded"
        }
    }

@app.get("/model-stats", tags=["System Monitoring"])
def get_model_stats(orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.get_model_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model stats: {e}")

@app.post("/api/encrypt-upload/")
async def upload_and_encrypt_file(file: UploadFile = File(...), sensitivity_score: float = 0.5):
    """
    Encrypts an uploaded file based on its sensitivity and stores it in cloud storage.
    """
    try:
        file_bytes = await file.read()
        
        # Call the encryption and upload function
        result = encrypt_and_upload_file(
            file_bytes=file_bytes,
            original_filename=file.filename,
            sensitivity=sensitivity_score
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": f"File '{file.filename}' encrypted and uploaded successfully.",
            "data": {
                "firestore_doc_id": result["firestore_doc_id"],
                "gcs_object_name": result["object_name"],
                "encryption_type": result["cipher"]
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encrypt and upload file: {str(e)}")

@app.get("/api/download-decrypt/")
async def download_and_decrypt_file(firestore_doc_id: str):
    """
    Retrieves and decrypts an encrypted file from cloud storage using its Firestore document ID.
    """
    try:
        plaintext, metadata = download_and_decrypt_file_by_doc(firestore_doc_id)
        
        return Response(content=plaintext, media_type="application/octet-stream", headers={
            "Content-Disposition": f'attachment; filename="{metadata["original_filename"]}"'
        })
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download and decrypt file: {str(e)}")

# Other existing endpoints can go here, e.g.,
# @app.get("/health-check/")
# async def health_check():
#     return {"status": "ok"}

# --- Include API Routers ---
# These handle user authentication and alerts.
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(users.router) # No prefix for the users router