import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
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
        if result.get("is_phishing", False) or result.get("status") == "Phishing":
            alert = alerting.format_phishing_alert(data.text, result)
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
        if result.get("is_injection", False) or result.get("status") == "Injection":
            alert = alerting.format_code_injection_alert(data.text, result)
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
    text: str = Form(None),
    file: UploadFile = File(None),
    orch: CybersecurityOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Performs comprehensive security analysis on the input text or uploaded file.
    Uses all available model artifacts for thorough analysis.
    """
    try:
        # Handle file upload
        if file and file.filename:
            file_content = await file.read()
            analysis_text = file_content.decode('utf-8', errors='ignore')
            file_metadata = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(file_content)
            }
        elif text:
            analysis_text = text
            file_metadata = None
        else:
            raise HTTPException(status_code=400, detail="Either text or file must be provided")

        print(f"Analyzing content of length: {len(analysis_text)} characters")

        # Run all analyses using model artifacts
        results = {}

        # 1. Sensitive Data Analysis (using data classification models)
        try:
            sensitive_result = orch.classify_sensitive_data(analysis_text)
            results["sensitive_data"] = sensitive_result
            print(f"Sensitive data analysis completed: {sensitive_result.get('classification', 'Unknown')}")
        except Exception as e:
            results["sensitive_data"] = {
                "error": f"Sensitive data analysis failed: {str(e)}",
                "classification": "ERROR"
            }
            print(f"Sensitive data analysis error: {e}")

        # 2. Data Quality Assessment (using quality assessment models)
        try:
            quality_result = orch.assess_data_quality(analysis_text)
            results["data_quality"] = quality_result
            print(f"Data quality analysis completed: {quality_result.get('quality_score', 0)}")
        except Exception as e:
            results["data_quality"] = {
                "error": f"Data quality analysis failed: {str(e)}",
                "quality_score": 0.0
            }
            print(f"Data quality analysis error: {e}")

        # 3. Phishing Detection (using transformer models)
        try:
            phishing_result = orch.detect_phishing(analysis_text)
            results["phishing"] = phishing_result
            print(f"Phishing analysis completed: {phishing_result.get('status', 'Unknown')}")
        except Exception as e:
            results["phishing"] = {
                "error": f"Phishing detection failed: {str(e)}",
                "status": "ERROR"
            }
            print(f"Phishing analysis error: {e}")

        # 4. Code Injection Detection (using transformer models)
        try:
            code_injection_result = orch.detect_code_injection(analysis_text)
            results["code_injection"] = code_injection_result
            print(f"Code injection analysis completed: {code_injection_result.get('status', 'Unknown')}, confidence: {code_injection_result.get('confidence', 0)}")
        except Exception as e:
            results["code_injection"] = {
                "error": f"Code injection detection failed: {str(e)}",
                "status": "ERROR"
            }
            print(f"Code injection analysis error: {e}")

        # 5. File-specific analysis (if file was uploaded)
        if file_metadata:
            try:
                import hashlib
                file_hash = hashlib.sha256(file_content).hexdigest()
                results["file_analysis"] = {
                    "file_hash": file_hash,
                    "file_size": file_metadata["size"],
                    "content_type": file_metadata["content_type"],
                    "filename": file_metadata["filename"]
                }
                print(f"File analysis completed: {file_hash[:16]}...")
            except Exception as e:
                results["file_analysis"] = {
                    "error": f"File analysis failed: {str(e)}"
                }
                print(f"File analysis error: {e}")

        # Calculate overall risk score
        risk_scores = []
        risk_weights = []

        # Sensitive data risk (weight: 0.4)
        if "error" not in results["sensitive_data"]:
            sensitive_conf = results["sensitive_data"].get("result", {}).get("confidence", 0)
            risk_scores.append(sensitive_conf)
            risk_weights.append(0.4)

        # Data quality risk (weight: 0.1)
        if "error" not in results["data_quality"]:
            quality_score = results["data_quality"].get("quality_score", 1.0)
            # Lower quality = higher risk
            quality_risk = 1.0 - quality_score
            risk_scores.append(quality_risk)
            risk_weights.append(0.1)

        # Phishing risk (weight: 0.3)
        if "error" not in results["phishing"]:
            phishing_status = results["phishing"].get("status", "")
            phishing_conf = results["phishing"].get("confidence", 0)
            # If phishing is detected, use confidence as risk; if safe, risk is 0
            phishing_risk = phishing_conf if phishing_status == "Phishing" else 0.0
            risk_scores.append(phishing_risk)
            risk_weights.append(0.3)

        # Code injection risk (weight: 0.2)
        if "error" not in results["code_injection"]:
            injection_status = results["code_injection"].get("status", "")
            injection_conf = results["code_injection"].get("confidence", 0)
            # If injection is detected, use confidence as risk; if safe, risk is 0
            injection_risk = injection_conf if injection_status == "Injection" else 0.0
            risk_scores.append(injection_risk)
            risk_weights.append(0.2)

        # Calculate weighted average
        if risk_scores and risk_weights:
            overall_risk = sum(score * weight for score, weight in zip(risk_scores, risk_weights))
            overall_risk = overall_risk / sum(risk_weights)
        else:
            overall_risk = 0.0

        alerts_created = []

        # Alert for sensitive data
        if "error" not in results["sensitive_data"]:
            sensitive_class = results["sensitive_data"].get("result", {}).get("classification", "")
            if sensitive_class in ["PII", "Financial", "Secrets", "SENSITIVE"]:
                alert = alerting.format_sensitive_data_alert(analysis_text, results["sensitive_data"])
                alert_result = await alerting.create_alert(alert)
                if alert_result.get("status") == "success":
                    alerts_created.append("sensitive_data")

        # Alert for phishing - IMPROVED LOGIC
        if "error" not in results["phishing"]:
            phishing_result = results["phishing"]
            phishing_status = phishing_result.get("status", "")
            is_phishing = phishing_result.get("is_phishing", False)
            
            # Check multiple indicators for phishing
            if phishing_status == "Phishing" or is_phishing:
                alert = alerting.format_phishing_alert(analysis_text, phishing_result)
                alert_result = await alerting.create_alert(alert)
                if alert_result.get("status") == "success":
                    alerts_created.append("phishing")
                    print(f"✅ Phishing alert created successfully")

        # Alert for code injection - FIXED LOGIC
        if "error" not in results["code_injection"]:
            injection_result = results["code_injection"]
            injection_status = injection_result.get("status", "")
            is_injection = injection_result.get("is_injection", False)
            confidence = injection_result.get("confidence", 0)
            
            # Check multiple indicators for code injection - FIXED LOGIC
            # Only create alerts for clear injection indicators, not for uncertain results
            injection_detected = (
                injection_status in ["Injection", "XSS", "SQL Injection", "Command Injection"] or
                is_injection or
                (confidence > 0.8 and injection_status == "Injection")  # Higher threshold and specific status
            )
            
            if injection_detected:
                print(f"🚨 Code injection detected! Status: {injection_status}, is_injection: {is_injection}, confidence: {confidence}")
                alert = alerting.format_code_injection_alert(analysis_text, injection_result)
                alert_result = await alerting.create_alert(alert)
                if alert_result.get("status") == "success":
                    alerts_created.append("code_injection")
                    print(f"✅ Code injection alert created successfully")
            else:
                print(f"ℹ️ No code injection detected. Status: {injection_status}, confidence: {confidence}, is_injection: {is_injection}")

        # Alert for poor data quality
        if "error" not in results["data_quality"]:
            quality_score = results["data_quality"].get("quality_score", 1.0)
            if quality_score < 0.7:
                alert = alerting.format_data_quality_alert(analysis_text, results["data_quality"])
                alert_result = await alerting.create_alert(alert)
                if alert_result.get("status") == "success":
                    alerts_created.append("data_quality")

        print(f"📊 Total alerts created: {len(alerts_created)} - {alerts_created}")

        return {
            "analysis_type": "Comprehensive Security Analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "overall_risk_score": overall_risk,
            "risk_level": _get_risk_level(overall_risk),
            "model_artifacts_used": {
                "sensitive_data_model": "error" not in results["sensitive_data"],
                "data_quality_model": "error" not in results["data_quality"],
                "phishing_model": "error" not in results["phishing"],
                "code_injection_model": "error" not in results["code_injection"]
            },
            "results": results,
            "alerts_created": alerts_created,
            "file_metadata": file_metadata
        }

    except Exception as e:
        print(f"Comprehensive analysis error: {e}")
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

@app.get("/files", tags=["Files"])
async def list_files():
    """
    Lists all file metadata from Firestore.
    """
    try:
        collection_ref = db.collection(FIRESTORE_COLLECTION)
        docs = collection_ref.stream()
        files = []
        for doc in docs:
            file_data = doc.to_dict()
            file_data['firestore_doc_id'] = doc.id
            files.append(file_data)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
# --- Include API Routers ---
app.include_router(alerts.router)
app.include_router(users.router)