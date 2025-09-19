from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# [CORRECTED] Use a relative import to go up one level from 'routers' to 'api'
try:
    from ..firebase_admin import db 
except (ImportError, ValueError):
    # This fallback can be helpful for direct script testing, but the relative one is key
    from api.firebase_admin import db

# --- Pydantic Models for Alerts ---
class AlertCreate(BaseModel):
    """Model for creating a new alert."""
    title: str = Field(..., example="Suspicious Network Activity")
    description: str = Field(..., example="High volume of outbound traffic detected from internal IP.")
    severity: str = Field(..., example="High", description="Can be 'Low', 'Medium', 'High', 'Critical'")
    source: str = Field(..., example="Network Intrusion Detector")
    details: Dict[str, Any] = Field({}, example={"ip_address": "192.168.1.100", "packets": 5000})

class Alert(AlertCreate):
    """Model for representing an alert retrieved from the database."""
    id: str
    timestamp: datetime
    is_read: bool = False

# --- API Router ---
router = APIRouter()

@router.post("/alerts/", response_model=Alert, status_code=201)
async def create_alert(alert_data: AlertCreate):
    """Creates a new alert and stores it in Firestore."""
    try:
        new_alert_ref = db.collection('alerts').document()
        alert_to_save = alert_data.dict()
        alert_to_save['timestamp'] = datetime.now()
        alert_to_save['is_read'] = False
        new_alert_ref.set(alert_to_save)
        response_data = alert_to_save.copy()
        response_data['id'] = new_alert_ref.id
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert in Firestore: {str(e)}")

@router.get("/alerts/", response_model=List[Alert])
async def get_alerts(limit: int = 100):
    """Retrieves a list of the latest alerts from Firestore."""
    try:
        alerts_ref = db.collection('alerts').order_by('timestamp', direction='DESCENDING').limit(limit)
        alerts = []
        for doc in alerts_ref.stream():
            alert_data = doc.to_dict()
            alert_data['id'] = doc.id
            alerts.append(alert_data)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts from Firestore: {str(e)}")

@router.put("/alerts/{alert_id}/read", status_code=204)
async def mark_alert_as_read(alert_id: str):
    """Marks a specific alert as read in Firestore."""
    try:
        alert_ref = db.collection('alerts').document(alert_id)
        doc = alert_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Alert not found")
        alert_ref.update({'is_read': True})
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert status in Firestore: {str(e)}")