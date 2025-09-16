from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime
from datetime import datetime
from api.database import Base  # Import Base from the central database file

class AnalysisResult(Base):
    """Analysis result model for storing file analysis results."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)
    file_type = Column(String(50), nullable=True)
    analysis_type = Column(String(50), nullable=False)
    is_malicious = Column(Boolean, default=False, nullable=False)
    confidence_score = Column(Float, nullable=True)
    analysis_details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(36), nullable=True, index=True)

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, file_name='{self.file_name}', is_malicious={self.is_malicious})>"
