"""Pytest fixtures for the CEO Tracker backend.

Overrides the FastAPI ``get_db`` dependency to use an in-memory SQLite database
(see testing_db.py). Production code is untouched.
"""
import pytest
from fastapi.testclient import TestClient

from testing_db import TestingSessionLocal, test_engine
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture()
def schema():
    """Create the schema for one test, then drop it."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session(schema):
    """Yield a session against the per-test schema."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(schema):
    """FastAPI TestClient with get_db overridden to the test database.

    Each request gets its own session (bound to the shared in-memory DB), so
    tests should ``commit()`` any data they seed via ``db_session``.
    """

    def _override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
