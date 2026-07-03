"""Smoke test for init_db.seed_database (seed-data integrity).

Verifies the seed helper populates the expected number of companies/CEOs
without depending on a production database: init_db's SessionLocal is
redirected to the in-memory test engine.
"""
from testing_db import TestingSessionLocal
from app.models import CEO, Company


def test_seed_database_populates_companies_and_ceos(db_session, monkeypatch):
    import init_db

    monkeypatch.setattr(init_db, "SessionLocal", TestingSessionLocal)

    init_db.seed_database()

    fresh = TestingSessionLocal()
    try:
        assert fresh.query(Company).count() == 25  # 20 tracked + 5 additional
        assert fresh.query(CEO).count() == 20  # one CEO per tracked company
        tracked = fresh.query(Company).filter(Company.is_tracked.is_(True)).count()
        assert tracked == 20
    finally:
        fresh.close()


def test_seed_database_is_idempotent(db_session, monkeypatch):
    import init_db

    monkeypatch.setattr(init_db, "SessionLocal", TestingSessionLocal)

    init_db.seed_database()
    init_db.seed_database()  # second run should skip (existing companies)

    fresh = TestingSessionLocal()
    try:
        assert fresh.query(Company).count() == 25
    finally:
        fresh.close()
