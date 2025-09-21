from datetime import datetime
from typing import Dict, Any, List

# Use a relative import to access the AlertCreate model from the sibling 'routers' directory
from .routers.alerts import AlertCreate 
from .firebase_admin import db

async def create_alert(alert_data: AlertCreate):
    """
    Creates a new alert and stores it in Firestore.
    This is the single point of entry for adding alerts to the database.
    """
    try:
        new_alert_ref = db.collection('alerts').document()
        alert_to_save = alert_data.dict()
        alert_to_save['timestamp'] = datetime.now()
        alert_to_save['is_read'] = False
        new_alert_ref.set(alert_to_save)
        print(f"Successfully created alert: {alert_data.title}")
        return {"status": "success", "alert_id": new_alert_ref.id}
    except Exception as e:
        print(f"FATAL: Failed to create alert in Firestore: {e}")
        return {"status": "error", "message": str(e)}

# --- Alert Formatting Functions ---

def format_phishing_alert(text: str, result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for a phishing detection event."""
    confidence_score = result.get('confidence', 0) * 100
    return AlertCreate(
        title="Phishing Attempt Detected",
        description=f"A potential phishing link was detected with {confidence_score:.2f}% confidence.",
        severity="High",
        source="Phishing Detection Model",
        details={
            "type": "phishing",
            "text_analyzed": text[:500],  # Truncate for brevity
            "confidence": result.get('confidence'),
            "recommendation": "Do not click any links or provide personal information. Delete the message immediately."
        }
    )

def format_code_injection_alert(text: str, result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for a code injection event."""
    score = result.get('score', 0)
    return AlertCreate(
        title="Code Injection Vulnerability",
        description=f"A potential code injection pattern was found with a threat score of {score:.2f}.",
        severity="Critical",
        source="Code Injection Detector",
        details={
            "type": "code_injection",
            "vulnerable_string": text,
            "score": score,
            "recommendation": "Ensure all user inputs are rigorously sanitized. Use parameterized queries or prepared statements for database interactions."
        }
    )

def format_malicious_file_alert(file_name: str, result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for a malicious file detection."""
    threat_type = result.get('threat_type', 'Unknown Threat')
    return AlertCreate(
        title="Malicious File Detected",
        description=f"The file '{file_name}' has been identified as a potential threat: {threat_type}.",
        severity="Critical",
        source="Static File Analyzer",
        details={
            "type": "malicious_file",
            "file_name": file_name,
            "threat_type": threat_type,
            "confidence": result.get('confidence'),
            "recommendation": "Quarantine or delete this file immediately. Do not execute or open it. Perform a full system scan."
        }
    )

def format_network_anomaly_alert(features: List[float], result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for anomalous network traffic."""
    return AlertCreate(
        title="Suspicious Network Activity",
        description="Network traffic patterns deviate significantly from the established baseline, indicating a potential intrusion.",
        severity="High",
        source="Network Anomaly Detector",
        details={
            "type": "network_anomaly",
            "reason": result.get('reason', 'Anomalous feature values detected.'),
            "traffic_features": features,
            "recommendation": "Investigate the source and destination IP addresses associated with this traffic. Check for unauthorized connections or data exfiltration."
        }
    )
    
def format_system_call_alert(call_sequence: List[int], result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for an anomalous system call sequence."""
    matched_pattern = result.get('matched_pattern', 'an unknown malicious behavior')
    return AlertCreate(
        title="Anomalous System Behavior",
        description=f"An unusual sequence of system calls was detected, matching a pattern for {matched_pattern}.",
        severity="High",
        source="Dynamic Behavior Analyzer",
        details={
            "type": "system_call_anomaly",
            "call_sequence": call_sequence,
            "matched_pattern": matched_pattern,
            "recommendation": "Isolate the affected system or process. Investigate running processes for unauthorized activity."
        }
    )

def format_sensitive_data_alert(text: str, result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for sensitive data exposure."""
    found_types = ", ".join(result.get('data_types_found', []))
    return AlertCreate(
        title="Sensitive Data Exposure",
        description=f"Personally Identifiable Information (PII) was detected. Types found: {found_types}.",
        severity="Medium",
        source="Data Classification Model",
        details={
            "type": "sensitive_data",
            "data_types_found": result.get('data_types_found', []),
            "source_text": text[:500], # Truncate for brevity
            "recommendation": "Review the data source to ensure this information is properly secured, redacted, or masked according to compliance policies."
        }
    )

def format_data_quality_alert(payload: Any, result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for poor data quality."""
    issues = ", ".join(result.get('issues', ['unknown issues']))
    return AlertCreate(
        title="Poor Data Quality Detected",
        description=f"Data quality assessment failed with a score of {result.get('quality_score', 0):.2f}. Issues: {issues}.",
        severity="Low",
        source="Data Quality Assessor",
        details={
            "type": "data_quality",
            "quality_score": result.get('quality_score'),
            "issues": result.get('issues', []),
            "recommendation": "Review the data ingestion pipeline. Ensure data is complete, consistent, and adheres to the expected format."
        }
    )