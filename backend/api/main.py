import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from google.cloud import storage
from datetime import datetime  # Add this import at the top of the file
from dotenv import load_dotenv
# --- Local Imports ---
from .orchestrator import CybersecurityOrchestrator
from .routers import users, alerts
from .firebase_admin import db
from . import alerting  # Import the new centralized alerting module
from .storage_handler import encrypt_and_upload_file, download_and_decrypt_file_by_doc
from fastapi.responses import JSONResponse, Response
# --- Global Orchestrator ---
orchestrator: CybersecurityOrchestrator = None

# Load environment variables from the .env file
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, '.env'))

# --- GCS Model Download Function ---
def download_models_from_gcs(bucket_name: str, destination_folder: str = "downloaded_models"):
    """
    Downloads all files from a specified GCS bucket to a local folder.
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
            os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
            blob.download_to_filename(destination_file_name)
            print(f"Successfully downloaded {blob.name} to {destination_file_name}")
        print("All models downloaded successfully.")

    except Exception as e:
        print(f"FATAL: An error occurred while downloading models: {e}")
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
    Handles downloading the ML models and initializing the orchestrator.
    """
    global orchestrator
    bucket_name = "realtime-data-sanitization-models"
    local_models_folder = "downloaded_models"
    download_models_from_gcs(bucket_name, local_models_folder)
    print("Initializing Cybersecurity Orchestrator...")
    orchestrator = CybersecurityOrchestrator(model_dir=local_models_folder)
    print("Orchestrator initialized. Models are ready to serve requests.")

# --- Dependency Injection for the Orchestrator ---
def get_orchestrator():
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator is not available.")
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
    data: Dict[str, Any]

class SystemCalls(BaseModel):
    call_sequence: List[int]

# --- API Endpoints ---

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Welcome to the AI Cybersecurity System API"}

@app.post("/analyze-dynamic-behavior", tags=["Threat Analysis"])
async def dynamic_analysis(data: DynamicData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.analyze_dynamic_behavior(data.call_sequence)
        # [MODIFIED] Create an alert if malicious behavior is detected
        if result.get("prediction") == "Malicious":
            alert = alerting.format_system_call_alert(data.call_sequence, result)
            await alerting.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-network-traffic", tags=["Threat Analysis"])
async def network_analysis(data: NetworkData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    EXPECTED_FEATURES = 10 
    if len(data.features) != EXPECTED_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid number of features. Expected {EXPECTED_FEATURES}, but got {len(data.features)}."
        )
    try:
        result = orch.analyze_network_traffic(data.features)
        # [MODIFIED] Create an alert if an anomaly is detected
        if result.get("prediction") == "Anomaly":
            alert = alerting.format_network_anomaly_alert(data.features, result)
            await alerting.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-text", tags=["Analysis"])
async def analyze_text(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        sensitive_result = orch.classify_sensitive_data(data.text)
        quality_result = orch.assess_data_quality(data.text)
        
        # [MODIFIED] Create alerts based on analysis
        if sensitive_result.get("has_sensitive_data"):
            alert = alerting.format_sensitive_data_alert(data.text, sensitive_result)
            await alerting.create_alert(alert)
        if quality_result.get("quality_score", 1.0) < 0.7: # Threshold for bad quality
            alert = alerting.format_data_quality_alert(data.text, quality_result)
            await alerting.create_alert(alert)

        return {
            "analysis_type": "Text Analysis",
            "sensitive_data_analysis": sensitive_result,
            "data_quality_analysis": quality_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during text analysis: {e}")

@app.post("/analyze-file", tags=["Analysis"])
async def analyze_file(file: UploadFile = File(...), orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    temp_dir = "tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = orch.analyze_file_for_threats(temp_file_path)

        # [MODIFIED] Create an alert if the file is malicious
        if result.get("is_malicious"):
            alert = alerting.format_malicious_file_alert(file.filename, result)
            await alerting.create_alert(alert)

        return {"analysis_type": "Static File Analysis", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during file analysis: {e}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/detect-phishing", tags=["Threat Detection"])
async def detect_phishing_endpoint(
    data: TextData, 
    orch: CybersecurityOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Endpoint to detect phishing attempts in the provided text.
    """
    try:
        result = orch.detect_phishing(data.text)
        
        # Create an alert if phishing is detected
        if result.get("is_phishing", False):
            alert = {
                "alert_type": "phishing_attempt",
                "severity": "high",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "suspicious_urls": result.get("suspicious_urls", []),
                    "confidence": result.get("confidence", 0),
                    "indicators": [
                        "suspicious_urls" if result.get("suspicious_urls") else None,
                        "urgency_keywords" if result.get("contains_urgency_keywords") else None,
                        "suspicious_sender" if result.get("suspicious_sender") else None
                    ]
                },
                "raw_text": data.text[:500]  # Store first 500 chars for reference
            }
            await alerting.create_alert(alert)
            
        return {
            "analysis_type": "Phishing Detection",
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in phishing detection: {str(e)}"
        )

@app.post("/detect-code-injection", tags=["Threat Detection"])
async def detect_code_injection_endpoint(
    data: TextData, 
    orch: CybersecurityOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Endpoint to detect code injection attempts in the provided text.
    """
    try:
        result = orch.detect_code_injection(data.text)
        
        # Create an alert if injection is detected
        if result.get("is_injection", False):
            alert = {
                "alert_type": "code_injection_attempt",
                "severity": "critical",
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "detected_patterns": result.get("detected_patterns", []),
                    "confidence": result.get("confidence", 0),
                    "severity_levels": list(set(
                        pattern.get("severity", "medium") 
                        for pattern in result.get("detected_patterns", [])
                    ))
                },
                "raw_text": data.text[:500]  # Store first 500 chars for reference
            }
            await alerting.create_alert(alert)
            
        return {
            "analysis_type": "Code Injection Detection",
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in code injection detection: {str(e)}"
        )
@app.post("/analyze-system-calls", tags=["Threat Detection"])
async def analyze_system_calls(data: SystemCalls, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.analyze_system_calls(data.call_sequence)
        # [MODIFIED] Create an alert for anomalous system call patterns
        if result.get("is_malicious"):
            alert = alerting.format_system_call_alert(data.call_sequence, result)
            await alerting.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify-sensitive-data", tags=["Data Classification"])
async def classify_sensitive_data(data: TextData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.classify_sensitive_data(data.text)
        # [MODIFIED] Create an alert if sensitive data is found
        if result.get("has_sensitive_data"):
            alert = alerting.format_sensitive_data_alert(data.text, result)
            await alerting.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-data-quality", tags=["Data Classification"])
async def assess_data_quality_features(data: QualityData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.assess_data_quality(data.features)
        # [MODIFIED] Create an alert for poor quality data
        if result.get("quality_score", 1.0) < 0.7:
            alert = alerting.format_data_quality_alert(data.features, result)
            await alerting.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-json-quality", tags=["Data Classification"])
async def assess_json_quality(payload: JsonData, orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        result = orch.assess_data_quality(payload.data)
        # [MODIFIED] Create an alert for poor quality JSON
        if result.get("quality_score", 1.0) < 0.7:
            alert = alerting.format_data_quality_alert(payload.data, result)
            await alerting.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON quality assessment failed: {e}")

# Add these endpoints to your existing comprehensive analysis
@app.post("/comprehensive-analysis", tags=["Analysis"])
async def comprehensive_analysis(
    data: TextData, 
    orch: CybersecurityOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Performs comprehensive security analysis on the input text.
    """
    try:
        # Run all analyses in parallel
        sensitive_result = orch.classify_sensitive_data(data.text)
        quality_result = orch.assess_data_quality(data.text)
        phishing_result = await detect_phishing_endpoint(data, orch)
        code_injection_result = await detect_code_injection_endpoint(data, orch)
        
        # Calculate overall risk score (weighted average with intelligent thresholds)
        risk_scores = [
            sensitive_result.get("result", {}).get("confidence", 0),
            quality_result.get("quality_score", 1.0),
            phishing_result.get("result", {}).get("confidence", 0),
            code_injection_result.get("result", {}).get("confidence", 0)
        ]

        # Apply intelligent weighting based on detection reliability
        weights = [0.3, 0.1, 0.3, 0.3]  # Sensitive data, Quality, Phishing, Code Injection

        # Additional intelligent analysis to detect obvious false positives
        false_positive_indicators = {
            'phishing': [
                len(data.text.split()) < 15,  # Short messages are unlikely to be phishing
                'name' in data.text.lower() and 'my' in data.text.lower(),  # Personal introductions
                not any(word in data.text.lower() for word in ['click', 'here', 'urgent', 'account', 'verify', 'login', 'http']),
            ],
            'code_injection': [
                not any(char in data.text for char in ['<', '>', ';', '$', '|', '&', '(', ')', '{', '}', '[', ']']),
                len(data.text.split()) < 20,  # Short text can't really contain dangerous code
                all(word.isalpha() or word in ['my', 'is', 'name'] for word in data.text.lower().split() if len(word) > 1),
            ]
        }

        # More precise false positive detection
        words = data.text.lower().split()
        is_personal_message = (
            'name' in data.text.lower() and
            'my' in data.text.lower() and
            len(words) < 15 and
            not any(word in words for word in ['urgent', 'verify', 'account', 'login', 'password', 'bank'])
        )

        is_normal_text = (
            len(words) < 20 and
            all(word.isalpha() or word in ['my', 'is', 'name', 'the', 'and', 'or', 'but'] for word in words if len(word) > 1)
        )

        # Override ML results only for obvious personal messages or normal text
        if is_personal_message or (is_normal_text and len(words) < 10):
            phishing_result["result"] = {"status": "Safe", "confidence": 0.05}

        if is_normal_text and len(words) < 15:
            code_injection_result["result"] = {"status": "Safe", "confidence": 0.05}

        # Recalculate with adjusted confidences
        adjusted_risk_scores = [
            sensitive_result.get("result", {}).get("confidence", 0),
            quality_result.get("quality_score", 1.0),
            phishing_result.get("result", {}).get("confidence", 0),
            code_injection_result.get("result", {}).get("confidence", 0)
        ]

        overall_risk = sum(score * weight for score, weight in zip(adjusted_risk_scores, weights))
        overall_risk = overall_risk / sum(weights) if sum(weights) > 0 else 0
        
        return {
            "analysis_type": "Comprehensive Security Analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "overall_risk_score": overall_risk,
            "risk_level": _get_risk_level(overall_risk),
            "analyses": {
                "sensitive_data": sensitive_result,
                "data_quality": quality_result,
                "phishing": phishing_result.get("result", {}),
                "code_injection": code_injection_result.get("result", {})
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in comprehensive analysis: {str(e)}"
        )

def _get_risk_level(score: float) -> str:
    """Convert risk score to human-readable level"""
    if score >= 0.8:
        return "critical"
    elif score >= 0.6:
        return "high"
    elif score >= 0.4:
        return "medium"
    elif score >= 0.2:
        return "low"
    return "info"


@app.get("/health", tags=["System Monitoring"])
async def health_check():
    db_status = "ok"
    try:
        db.collection('health_check').document('status').get()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "components": {
            "database": db_status,
            "orchestrator_status": "loaded" if orchestrator else "not_loaded"
        }
    }

# Add this entire block to your main.py file

@app.get("/test-alert", tags=["Testing"])
async def create_test_alert():
    """
    Creates a sample alert for testing purposes.
    This endpoint is used by the test script to verify alert creation.
    """
    try:
        print("Received request to create a test alert...")
        test_alert_data = alerting.AlertCreate(
            title="Test: Phishing Attempt",
            description="This is a test alert generated for debugging.",
            severity="High",
            source="Test Endpoint",
            details={
                "type": "phishing",
                "text_analyzed": "http://test-phishing-site.com/login",
                "confidence": 0.95,
                "recommendation": "This is only a test. No action is needed."
            }
        )
        result = await alerting.create_alert(test_alert_data)
        if result["status"] == "success":
            return {"message": "Test alert created successfully", "alert_id": result["alert_id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to write test alert to database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating test alert: {e}")

        
@app.get("/model-stats", tags=["System Monitoring"])
def get_model_stats(orch: CybersecurityOrchestrator = Depends(get_orchestrator)):
    try:
        return orch.get_model_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model stats: {e}")

@app.post("/encrypt-upload")
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

@app.get("/download-decrypt")
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

# --- Include API Routers ---
app.include_router(alerts.router)
app.include_router(users.router)