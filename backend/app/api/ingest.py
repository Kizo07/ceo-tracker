"""
API endpoints for data ingestion.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..db.database import get_db
from ..services.ner import get_ner_service, KNOWN_COMPANIES
from ..services.sentiment import get_sentiment_service
from ..models import Company, CEO, Source, Speech, CompanyMention

router = APIRouter()


class IngestRequest(BaseModel):
    """Request model for manual ingestion."""
    text: str
    ceo_id: int
    source_type: str = "manual"
    title: Optional[str] = None
    url: Optional[str] = None


class IngestResponse(BaseModel):
    """Response model for ingestion results."""
    success: bool
    message: str
    mentions_created: int
    speech_id: Optional[int] = None


@router.post("/ingest", response_model=IngestResponse)
def ingest_text(
    request: IngestRequest,
    db: Session = Depends(get_db)
):
    """
    Manually ingest text for analysis.

    This endpoint allows manual submission of text (e.g., CEO quotes, press releases)
    for NER and sentiment analysis.
    """
    # Verify CEO exists
    ceo = db.query(CEO).filter(CEO.id == request.ceo_id).first()
    if not ceo:
        raise HTTPException(status_code=404, detail="CEO not found")

    # Create source record
    source = Source(
        url=request.url,
        title=request.title,
        source_type=request.source_type,
        provider="manual",
        raw_text=request.text,
        processed=False,
    )
    db.add(source)
    db.flush()

    # Create speech record
    speech = Speech(
        source_id=source.id,
        ceo_id=request.ceo_id,
        quote_text=request.text,
    )
    db.add(speech)
    db.flush()

    # Get NER service
    ner_service = get_ner_service()

    # Extract company mentions
    mentions = ner_service.extract_company_mentions(
        text=request.text,
        known_companies=KNOWN_COMPANIES,
    )

    # Get sentiment service
    sentiment_service = get_sentiment_service()

    mentions_created = 0

    for mention_data in mentions:
        # Find or create company (check by name or ticker)
        company = db.query(Company).filter(
            (Company.name == mention_data["company"]) | (Company.ticker == mention_data["ticker"])
        ).first()

        if not company:
            company = Company(
                name=mention_data["company"],
                ticker=mention_data["ticker"],
                is_tracked=False,
            )
            db.add(company)
            db.flush()

        # Analyze sentiment for the context
        sentiment_result = sentiment_service.analyze_sentiment(
            text=mention_data["context"]
        )

        # Create company mention
        company_mention = CompanyMention(
            speech_id=speech.id,
            mentioned_company_id=company.id,
            context_text=mention_data["context"],
            sentiment=sentiment_result["sentiment"],
            sentiment_confidence=sentiment_result["confidence"],
        )
        db.add(company_mention)
        mentions_created += 1

    # Mark source as processed
    source.processed = True

    db.commit()

    return IngestResponse(
        success=True,
        message=f"Successfully processed text. Found {mentions_created} company mentions.",
        mentions_created=mentions_created,
        speech_id=speech.id,
    )


@router.post("/ingest/test")
def test_ingestion(db: Session = Depends(get_db)):
    """
    Test endpoint that ingests a sample text.
    """
    # Find a CEO (preferably Jensen Huang)
    ceo = db.query(CEO).filter(CEO.name.ilike("%Jensen%")).first()

    if not ceo:
        # Create sample CEO
        company = db.query(Company).filter(Company.ticker == "NVDA").first()
        if not company:
            company = Company(name="NVIDIA", ticker="NVDA", is_tracked=True)
            db.add(company)
            db.flush()

        ceo = CEO(
            name="Jensen Huang",
            company_id=company.id,
            title="CEO",
        )
        db.add(ceo)
        db.flush()

    # Sample text about company mentions
    sample_text = """
    We're excited about the AI infrastructure landscape. Companies like Marvell Technologies
    are doing excellent work in the networking space. Their expertise in data center
    connectivity is impressive. However, we've seen some disappointing execution from
    certain competitors in the AI chip market. AMD has made progress but they still
    face significant challenges in manufacturing capacity. Intel's struggles continue
    as they try to pivot their business model.
    """

    request = IngestRequest(
        text=sample_text,
        ceo_id=ceo.id,
        source_type="test",
        title="Test CEO Speech",
    )

    return ingest_text(request, db)


@router.get("/ingest/status")
def get_ingestion_status(db: Session = Depends(get_db)):
    """Get ingestion status statistics."""
    total_sources = db.query(Source).count()
    processed_sources = db.query(Source).filter(Source.processed == True).count()
    pending_sources = total_sources - processed_sources

    return {
        "total_sources": total_sources,
        "processed_sources": processed_sources,
        "pending_sources": pending_sources,
        "processing_rate": f"{processed_sources / total_sources * 100:.1f}%" if total_sources > 0 else "0%",
    }
