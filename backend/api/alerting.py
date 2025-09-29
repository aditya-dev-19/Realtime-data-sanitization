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
    # Handle both 'confidence' and nested response formats
    confidence = result.get('confidence', 0)
    if 'result' in result and isinstance(result['result'], dict):
        confidence = result['result'].get('confidence', confidence)
    
    confidence_score = confidence * 100

    details = {
        "type": "phishing",
        "text_analyzed": text[:500],
        "confidence": confidence,
        "recommendation": "Do not click any links or provide personal information. Delete the message immediately."
    }

    # Add indicators from various possible locations
    if 'details' in result:
        details.update(result['details'])
    if 'indicators_found' in result.get('details', {}):
        details["indicators"] = result['details']['indicators_found']
    if 'suspicious_urls' in result:
        details["suspicious_urls"] = result['suspicious_urls']

    return AlertCreate(
        title="Phishing Attempt Detected",
        description=f"A potential phishing link was detected with {confidence_score:.2f}% confidence.",
        severity="High",
        source="Phishing Detection Model",
        details=details
    )

# Replace the format_code_injection_alert function in backend/api/alerting.py

def format_code_injection_alert(text: str, result: Dict[str, Any]) -> AlertCreate:
    """Formats an alert for a code injection event."""
    # Handle both ML model results (score/confidence) and rule-based results
    score = result.get('score', result.get('confidence', 0))
    status = result.get('status', 'Unknown')
    
    # Get patterns from various possible locations
    patterns = []
    if 'patterns_found' in result:
        patterns = result['patterns_found']
    elif 'details' in result:
        details = result['details']
        if isinstance(details, dict):
            patterns = details.get('patterns_found', details.get('detected_patterns', []))
    elif 'detected_patterns' in result:
        patterns = result['detected_patterns']
    
    # Ensure patterns is a list
    if not isinstance(patterns, list):
        patterns = []
    
    # Get severity from result or determine from confidence
    severity = result.get('severity', 'unknown')
    if severity == 'unknown':
        if score >= 0.8:
            severity = 'critical'
        elif score >= 0.6:
            severity = 'high'
        elif score >= 0.4:
            severity = 'medium'
        else:
            severity = 'low'
    
    # Build description
    if patterns:
        description = f"A potential code injection pattern was found with a threat score of {score:.2f}. Detected {len(patterns)} suspicious pattern(s)."
    else:
        description = f"A potential code injection threat was detected with a confidence of {score:.2f}."
    
    # Build details dict
    details_dict = {
        "type": "code_injection",
        "vulnerable_string": text[:500],  # Truncate for safety
        "score": float(score),
        "confidence": float(score),
        "status": status,
        "severity": severity,
        "recommendation": "Ensure all user inputs are rigorously sanitized. Use parameterized queries or prepared statements for database interactions."
    }
    
    # Add patterns if found
    if patterns:
        details_dict["patterns_found"] = patterns[:10]  # Limit to first 10
        if len(patterns) > 10:
            details_dict["additional_patterns_count"] = len(patterns) - 10
    
    # Add any additional info from ML model or rule-based detector
    if 'details' in result and isinstance(result['details'], dict):
        for key in ['fallback_used', 'ml_prediction', 'rule_based_prediction']:
            if key in result['details']:
                details_dict[key] = result['details'][key]
    
    return AlertCreate(
        title="Code Injection Vulnerability Detected",
        description=description,
        severity="Critical" if score >= 0.7 else "High",
        source="Code Injection Detector",
        details=details_dict
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