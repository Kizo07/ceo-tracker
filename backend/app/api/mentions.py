"""
API endpoints for company mentions.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel

from ..db.database import get_db
from ..models import CompanyMention, Company, CEO, Speech

router = APIRouter()


class MentionResponse(BaseModel):
    """Response model for a company mention."""
    id: int
    ceo_id: Optional[int]
    ceo_name: str
    ceo_company: str
    mentioned_company: str
    mentioned_ticker: Optional[str]
    context: str
    sentiment: Optional[str]
    confidence: Optional[float]
    relationship_type: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class MentionListResponse(BaseModel):
    """Response model for a list of mentions."""
    mentions: List[MentionResponse]
    total: int
    page: int
    page_size: int


@router.get("/mentions", response_model=MentionListResponse)
def get_mentions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ceo_id: Optional[int] = None,
    company_ticker: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of company mentions.

    Filters:
    - ceo_id: Filter by specific CEO
    - company_ticker: Filter by mentioned company ticker
    - sentiment: Filter by sentiment (positive/negative/neutral)
    """
    query = db.query(CompanyMention)

    if ceo_id:
        query = query.join(Speech).filter(Speech.ceo_id == ceo_id)

    if company_ticker:
        query = query.join(Company).filter(Company.ticker == company_ticker)

    if sentiment:
        query = query.filter(CompanyMention.sentiment == sentiment)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    mentions = query.order_by(CompanyMention.created_at.desc()).offset(offset).limit(page_size).all()

    # Build response
    mention_responses = []
    for mention in mentions:
        company = db.query(Company).filter(Company.id == mention.mentioned_company_id).first()

        # For mentions from speeches (CEO speaking about other companies)
        if mention.speech_id:
            speech = db.query(Speech).filter(Speech.id == mention.speech_id).first()
            if speech:
                ceo = db.query(CEO).filter(CEO.id == speech.ceo_id).first()
                ceo_id = ceo.id if ceo else None
                ceo_name = ceo.name if ceo else "Unknown"
                ceo_company = ""
                if ceo and ceo.company:
                    ceo_company_obj = db.query(Company).filter(Company.id == ceo.company_id).first()
                    ceo_company = ceo_company_obj.name if ceo_company_obj else ""
            else:
                # Speech was deleted
                ceo_id = None
                ceo_name = "Unknown"
                ceo_company = ""
        else:
            # For mentions from RSS feeds (press releases)
            # These don't have a CEO speaker - they're company communications
            ceo_id = None
            ceo_name = company.name if company else "Unknown"
            ceo_company = company.name if company else ""

        mention_responses.append(MentionResponse(
            id=mention.id,
            ceo_id=ceo_id,
            ceo_name=ceo_name,
            ceo_company=ceo_company,
            mentioned_company=company.name if company else "Unknown",
            mentioned_ticker=company.ticker if company else None,
            context=mention.context_text,
            sentiment=mention.sentiment,
            confidence=mention.sentiment_confidence,
            relationship_type=mention.relationship_type,
            created_at=mention.created_at.isoformat(),
        ))

    return MentionListResponse(
        mentions=mention_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/mentions/ceo/{ceo_id}", response_model=List[MentionResponse])
def get_ceo_mentions(ceo_id: int, db: Session = Depends(get_db)):
    """Get all mentions by a specific CEO."""
    mentions = db.query(CompanyMention)\
        .join(Speech)\
        .filter(Speech.ceo_id == ceo_id)\
        .order_by(CompanyMention.created_at.desc())\
        .all()

    responses = []
    for mention in mentions:
        speech = db.query(Speech).filter(Speech.id == mention.speech_id).first()
        ceo = db.query(CEO).filter(CEO.id == speech.ceo_id).first()
        company = db.query(Company).filter(Company.id == mention.mentioned_company_id).first()

        responses.append(MentionResponse(
            id=mention.id,
            ceo_id=ceo.id,
            ceo_name=ceo.name,
            ceo_company="",
            mentioned_company=company.name,
            mentioned_ticker=company.ticker,
            context=mention.context_text,
            sentiment=mention.sentiment,
            confidence=mention.sentiment_confidence,
            relationship_type=mention.relationship_type,
            created_at=mention.created_at.isoformat(),
        ))

    return responses


@router.get("/mentions/company/{ticker}", response_model=List[MentionResponse])
def get_company_mentions(ticker: str, db: Session = Depends(get_db)):
    """Get all mentions of a specific company by ticker."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")

    mentions = db.query(CompanyMention)\
        .filter(CompanyMention.mentioned_company_id == company.id)\
        .order_by(CompanyMention.created_at.desc())\
        .all()

    responses = []
    for mention in mentions:
        # Get CEO info if this mention is from a speech
        if mention.speech_id:
            speech = db.query(Speech).filter(Speech.id == mention.speech_id).first()
            if speech:
                ceo = db.query(CEO).filter(CEO.id == speech.ceo_id).first()
                ceo_id = ceo.id if ceo else None
                ceo_name = ceo.name if ceo else "Unknown"
                ceo_company = ""
            else:
                ceo_id = None
                ceo_name = "Unknown"
                ceo_company = ""
        else:
            # RSS press release - no CEO speaker
            ceo_id = None
            ceo_name = company.name if company else "Unknown"
            ceo_company = company.name if company else ""

        responses.append(MentionResponse(
            id=mention.id,
            ceo_id=ceo_id,
            ceo_name=ceo_name,
            ceo_company=ceo_company,
            mentioned_company=company.name,
            mentioned_ticker=company.ticker,
            context=mention.context_text,
            sentiment=mention.sentiment,
            confidence=mention.sentiment_confidence,
            relationship_type=mention.relationship_type,
            created_at=mention.created_at.isoformat(),
        ))

    return responses


@router.get("/sentiment/summary/{ceo_id}")
def get_sentiment_summary(ceo_id: int, db: Session = Depends(get_db)):
    """Get sentiment breakdown for a specific CEO."""
    mentions = db.query(CompanyMention)\
        .join(Speech)\
        .filter(Speech.ceo_id == ceo_id)\
        .all()

    summary = {
        "total": len(mentions),
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "unknown": 0
    }

    for mention in mentions:
        sentiment = mention.sentiment or "unknown"
        if sentiment in summary:
            summary[sentiment] += 1

    return summary
