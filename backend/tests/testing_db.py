"""Shared test-database plumbing.

Importable from both conftest.py and individual test modules (importing
conftest directly is a pytest anti-pattern). Forces an in-memory SQLite DB,
shared across connections/threads via StaticPool so TestClient (which runs
sync endpoints in a threadpool) sees the same data.
"""
import os

# Must be set BEFORE app.db.database (and thus Settings) is imported.
os.environ.setdefault("DATABASE_URL", "sqlite://")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
