"""
API endpoints for dashboard statistics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict

from ..db.database import get_db
from ..models import CompanyMention, Company, CEO, Speech

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics model."""
    total_mentions: int
    total_ceos: int
    total_companies: int
    sentiment_breakdown: Dict[str, int]
    recent_mentions: int
    most_mentioned_companies: List[Dict]
    most_active_ceos: List[Dict]


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall dashboard statistics."""
    # Total counts
    total_mentions = db.query(CompanyMention).count()
    total_ceos = db.query(CEO).count()
    total_companies = db.query(Company).filter(Company.is_tracked.is_(True)).count()

    # Sentiment breakdown
    sentiment_results = db.query(
        CompanyMention.sentiment,
        func.count(CompanyMention.id)
    ).group_by(CompanyMention.sentiment).all()

    sentiment_breakdown = {s[0] or "unknown": s[1] for s in sentiment_results}

    # Recent mentions (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_mentions = db.query(CompanyMention)\
        .filter(CompanyMention.created_at >= week_ago)\
        .count()

    # Most mentioned companies
    most_mentioned = db.query(
        Company.name,
        Company.ticker,
        func.count(CompanyMention.id).label('count')
    ).join(CompanyMention, Company.id == CompanyMention.mentioned_company_id)\
     .group_by(Company.id, Company.name, Company.ticker)\
     .order_by(func.count(CompanyMention.id).desc())\
     .limit(10)\
     .all()

    most_mentioned_companies = [
        {"name": m[0], "ticker": m[1], "count": m[2]}
        for m in most_mentioned
    ]

    # Most active CEOs (by speeches count)
    most_active = db.query(
        CEO.name,
        Company.name.label('company'),
        func.count(Speech.id).label('count')
    ).join(Company, CEO.company_id == Company.id)\
     .join(Speech, CEO.id == Speech.ceo_id)\
     .group_by(CEO.id, CEO.name, Company.name)\
     .order_by(func.count(Speech.id).desc())\
     .limit(10)\
     .all()

    most_active_ceos = [
        {"name": m[0], "company": m[1], "speeches": m[2]}
        for m in most_active
    ]

    return DashboardStats(
        total_mentions=total_mentions,
        total_ceos=total_ceos,
        total_companies=total_companies,
        sentiment_breakdown=sentiment_breakdown,
        recent_mentions=recent_mentions,
        most_mentioned_companies=most_mentioned_companies,
        most_active_ceos=most_active_ceos,
    )


@router.get("/timeline")
def get_timeline(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get chronological feed of mentions."""
    mentions = db.query(CompanyMention)\
        .order_by(CompanyMention.created_at.desc())\
        .limit(limit)\
        .all()

    timeline = []
    for mention in mentions:
        speech = db.query(Speech).filter(Speech.id == mention.speech_id).first()
        ceo = db.query(CEO).filter(CEO.id == speech.ceo_id).first()
        company = db.query(Company).filter(Company.id == mention.mentioned_company_id).first()

        timeline.append({
            "id": mention.id,
            "ceo": ceo.name,
            "mentioned_company": company.name,
            "ticker": company.ticker,
            "context": mention.context_text,
            "sentiment": mention.sentiment,
            "created_at": mention.created_at.isoformat(),
        })

    return timeline


@router.get("/dashboard/sentiment/{sentiment}")
def get_sentiment_companies(sentiment: str, db: Session = Depends(get_db)):
    """Get companies mentioned with specific sentiment."""
    results = db.query(
        Company.name,
        Company.ticker,
        func.count(CompanyMention.id).label('count')
    ).join(CompanyMention, Company.id == CompanyMention.mentioned_company_id)\
     .filter(CompanyMention.sentiment == sentiment)\
     .group_by(Company.id, Company.name, Company.ticker)\
     .order_by(func.count(CompanyMention.id).desc())\
     .all()

    return [{"name": r[0], "ticker": r[1], "count": r[2]} for r in results]
