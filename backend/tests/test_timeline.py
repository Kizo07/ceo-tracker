"""Regression guard for BUG-001: /api/timeline crashes on RSS-sourced mentions.

RSS/press-release mentions have ``speech_id IS NULL`` (ingestion.py sets
speech=None). The timeline handler dereferences ``speech.ceo_id`` without a
None-check (dashboard.py:107-108) and 500s.

This test is marked ``xfail(strict=True)`` so CI stays green while documenting
the defect; Phase 1 flips it to green and removes the marker.
"""
import pytest

from app.models import Company, CompanyMention


@pytest.mark.xfail(strict=True, reason="BUG-001: timeline crashes on NULL speech_id")
def test_timeline_handles_null_speech(client, db_session):
    company = Company(name="Marvell Technology", ticker="MRVL", is_tracked=False)
    db_session.add(company)
    db_session.flush()

    # Press-release mention: speech_id is NULL (the trigger for BUG-001).
    db_session.add(
        CompanyMention(
            mentioned_company_id=company.id,
            speech_id=None,
            context_text="Marvell mentioned in a press release.",
            sentiment="neutral",
            sentiment_confidence=0.9,
        )
    )
    db_session.commit()

    resp = client.get("/api/timeline")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["mentioned_company"] == "Marvell Technology"
