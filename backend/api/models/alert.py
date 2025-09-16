from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, func
import enum
from datetime import datetime
from api.database import Base  # Import Base from the central database file

class AlertSeverity(str, enum.Enum):    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class AlertType(str, enum.Enum):
    THREAT_DETECTED = "threat_detected"
    SYSTEM_ISSUE = "system_issue"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_ISSUE = "performance_issue"
    CONFIGURATION_CHANGE = "configuration_change"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.MEDIUM)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.OPEN)
    alert_type = Column(Enum(AlertType), nullable=False)
    source = Column(String(100), nullable=True)
    alert_metadata = Column('metadata', Text, nullable=True)  # JSON string for additional data (renamed to avoid conflict with SQLAlchemy)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "status": self.status.value,
            "type": self.alert_type.value,
            "source": self.source,
            "metadata": self.alert_metadata,  # Updated to use the new attribute name
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }
