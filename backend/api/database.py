from sqlalchemy import create_engine, MetaData, Column, Integer, String, Boolean, Float, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
import os
from contextlib import contextmanager
from typing import Generator
from datetime import datetime

# This is the declarative base class that all models will inherit from
# Using metadata with a specific naming convention to avoid conflicts
metadata = MetaData(
    naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Create the declarative base with our metadata
Base = declarative_base(metadata=metadata)

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

# Import all models here to ensure they're registered with SQLAlchemy
# This needs to be after Base is defined and before create_all()
# Import will be done in the models/__init__.py file

# This file should be imported before any models to ensure Base is defined first
# To initialize the database, import this module and call init_db() after all models are imported
