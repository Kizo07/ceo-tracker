"""
Database configuration and session management for CEO Tracker.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings
from typing import Generator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    database_url: str = "postgresql://ceo_tracker:password@localhost:5432/ceo_tracker"
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env


settings = Settings()

# Create SQLAlchemy engine
# For SQLite, we need to connect_args
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database sessions.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
