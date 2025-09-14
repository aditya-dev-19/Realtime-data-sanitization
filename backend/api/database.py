from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database URL (SQLite for simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./cybersecurity.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisResult(Base):
	__tablename__ = "analysis_results"

	id = Column(Integer, primary_key=True, index=True)
	file_name = Column(String)
	file_hash = Column(String, nullable=True)
	file_type = Column(String, nullable=True)
	analysis_type = Column(String)
	is_malicious = Column(Boolean)
	confidence_score = Column(Float, nullable=True)
	analysis_details = Column(String)  # JSON string
	timestamp = Column(DateTime, default=datetime.utcnow)
	user_id = Column(String, nullable=True)  # For future user tracking

# Dependency for FastAPI
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
