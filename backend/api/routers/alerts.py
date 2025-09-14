from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from database import get_db
from models.alert import Alert, AlertSeverity, AlertStatus, AlertType

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)

def create_alert(
    db: Session,
    title: str,
    alert_type: AlertType,
    severity: AlertSeverity = AlertSeverity.MEDIUM,
    description: str = None,
    source: str = None,
    metadata: dict = None,
):
    """Helper function to create a new alert."""
    alert = Alert(
        title=title,
        description=description,
        severity=severity,
        alert_type=alert_type,
        source=source or "system",
        metadata=json.dumps(metadata) if metadata else None,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

@router.get("/", response_model=List[dict])
def get_alerts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    days: Optional[int] = 7,
):
    """
    Retrieve a list of alerts with optional filtering.
    """
    query = db.query(Alert)
    
    # Apply filters
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if days:
        time_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Alert.created_at >= time_threshold)
    
    # Order by most recent first
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return [alert.to_dict() for alert in alerts]

@router.get("/{alert_id}", response_model=dict)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific alert by ID.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert.to_dict()

@router.put("/{alert_id}/status")
def update_alert_status(
    alert_id: int, 
    status: AlertStatus,
    db: Session = Depends(get_db)
):
    """
    Update the status of an alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = status
    if status == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.utcnow()
    
    db.commit()
    return {"message": f"Alert {alert_id} status updated to {status}"}

@router.post("/test/generate")
def generate_test_alerts(db: Session = Depends(get_db)):
    """
    Generate test alerts (for development only).
    """
    from faker import Faker
    import random
    
    fake = Faker()
    
    alert_types = list(AlertType)
    severities = list(AlertSeverity)
    statuses = list(AlertStatus)
    
    for _ in range(10):
        alert_type = random.choice(alert_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        # Create alert with realistic data based on type
        if alert_type == AlertType.THREAT_DETECTED:
            title = f"Potential {fake.word().capitalize()} Threat Detected"
            description = fake.sentence()
        elif alert_type == AlertType.SYSTEM_ISSUE:
            title = f"System {fake.word().capitalize()} Issue Detected"
            description = f"{fake.sentence()} Error code: {fake.uuid4()[:8]}"
        else:
            title = fake.sentence(nb_words=6)
            description = fake.paragraph()
        
        create_alert(
            db=db,
            title=title,
            description=description,
            alert_type=alert_type,
            severity=severity,
            source=fake.word(),
            metadata={"test_data": True, "priority": random.randint(1, 5)},
        )
    
    return {"message": "Generated 10 test alerts"}
