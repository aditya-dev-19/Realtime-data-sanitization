from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from datetime import datetime
import os
from contextlib import contextmanager
from typing import Generator

# Database URL (SQLite for development, use environment variable for production)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cybersecurity.db")

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session for thread safety
ScopedSession = scoped_session(SessionLocal)

# Base class for models
Base = declarative_base()

# Import models to ensure they're registered with SQLAlchemy
from models.alert import Alert  # noqa

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_hash = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    analysis_type = Column(String)
    is_malicious = Column(Boolean)
    confidence_score = Column(Float, nullable=True)
    analysis_details = Column(Text)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, nullable=True)  # For future user tracking

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, file_name='{self.file_name}')>"

# Dependency for FastAPI
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Session: A SQLAlchemy database session.
    """
    db = ScopedSession()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

# Create tables if they don't exist
if __name__ == "__main__":
    init_db()
