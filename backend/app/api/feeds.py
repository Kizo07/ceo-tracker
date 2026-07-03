"""
API endpoints for RSS feed management and monitoring.

Provides endpoints to trigger, monitor, and configure RSS feed ingestion.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict

from ..db.database import get_db
from ..services.feeds import get_feed_service, FeedConfig
from ..services.ingestion import IngestionService
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from workers.tasks import fetch_rss_feed, fetch_all_feeds

router = APIRouter()


class FeedStatusResponse(BaseModel):
    """Response model for feed status."""
    feed_key: str
    name: str
    ticker: str
    url: str
    provider: str
    last_fetched: Optional[str] = None
    entries_count: Optional[int] = None


class FeedListResponse(BaseModel):
    """Response model for feed list."""
    feeds: List[FeedStatusResponse]
    total_feeds: int


class TriggerFeedRequest(BaseModel):
    """Request model for triggering a single feed."""
    feed_key: str


class TriggerFeedResponse(BaseModel):
    """Response model for feed trigger."""
    success: bool
    message: str
    task_id: Optional[str] = None


class RefreshFeedsResponse(BaseModel):
    """Response model for refreshing all feeds."""
    success: bool
    message: str
    total_entries: Optional[int] = None
    total_mentions: Optional[int] = None


@router.get("/feeds/config", response_model=FeedListResponse)
def get_feed_config():
    """
    Get all configured RSS feeds.

    Returns a list of all RSS feed configurations.
    """
    feed_service = get_feed_service()
    feeds = feed_service.get_feeds()

    feed_statuses = []
    for key, config in feeds.items():
        feed_statuses.append(FeedStatusResponse(
            feed_key=key,
            name=config.name,
            ticker=config.ticker,
            url=config.url,
            provider=config.provider,
        ))

    return FeedListResponse(
        feeds=feed_statuses,
        total_feeds=len(feed_statuses),
    )


@router.get("/feeds/status")
def get_feeds_status(db: Session = Depends(get_db)):
    """
    Get status of all RSS feeds including entry counts.

    Returns statistics about each feed including how many entries
    have been processed from each source.
    """
    from ..models import Source

    feed_service = get_feed_service()
    feeds = feed_service.get_feeds()

    feed_statuses = []
    for key, config in feeds.items():
        # Count sources from this feed
        sources_count = db.query(Source).filter(
            Source.provider == config.provider,
            Source.source_type == "press_release",
        ).count()

        # Get most recent source from this feed
        latest_source = db.query(Source).filter(
            Source.provider == config.provider,
            Source.source_type == "press_release",
        ).order_by(Source.published_at.desc()).first()

        feed_statuses.append({
            "feed_key": key,
            "name": config.name,
            "ticker": config.ticker,
            "url": config.url,
            "provider": config.provider,
            "entries_count": sources_count,
            "last_fetched": latest_source.published_at.isoformat() if latest_source else None,
        })

    return {
        "feeds": feed_statuses,
        "total_feeds": len(feeds),
    }


@router.post("/feeds/trigger", response_model=TriggerFeedResponse)
def trigger_feed(
    request: TriggerFeedRequest,
    background_tasks: BackgroundTasks,
):
    """
    Manually trigger fetch for a single RSS feed.

    This is useful for testing or immediate updates.
    The task runs in the background.
    """
    feed_service = get_feed_service()
    feed_config = feed_service.get_feed(request.feed_key)

    if not feed_config:
        raise HTTPException(status_code=404, detail=f"Feed not found: {request.feed_key}")

    # Trigger the background task
    task = fetch_rss_feed.apply_async(args=[request.feed_key])

    return TriggerFeedResponse(
        success=True,
        message=f"Feed {request.feed_key} triggered for processing",
        task_id=task.id,
    )


@router.post("/feeds/refresh", response_model=RefreshFeedsResponse)
def refresh_all_feeds(background_tasks: BackgroundTasks):
    """
    Refresh all RSS feeds immediately.

    Triggers background processing for all configured feeds.
    """
    feed_service = get_feed_service()
    feeds = feed_service.get_feeds()

    if not feeds:
        raise HTTPException(status_code=404, detail="No feeds configured")

    # Trigger the background task
    task = fetch_all_feeds.apply_async()

    return RefreshFeedsResponse(
        success=True,
        message=f"Triggered {len(feeds)} feeds for processing",
        task_id=task.id,
    )


@router.post("/feeds/test")
def test_feed_fetch(feed_key: str, db: Session = Depends(get_db)):
    """
    Test endpoint to fetch and preview a single feed without saving.

    Useful for debugging feed configuration.
    """
    feed_service = get_feed_service()
    feed_config = feed_service.get_feed(feed_key)

    if not feed_config:
        raise HTTPException(status_code=404, detail=f"Feed not found: {feed_key}")

    # Fetch the feed (synchronous, limited entries)
    entries = feed_service.fetch_feed(feed_config.url, max_entries=5)

    return {
        "feed_key": feed_key,
        "feed_config": {
            "name": feed_config.name,
            "ticker": feed_config.ticker,
            "url": feed_config.url,
        },
        "entries_fetched": len(entries),
        "entries": [
            {
                "title": entry.title,
                "url": entry.url,
                "published_at": entry.published_at.isoformat() if entry.published_at else None,
                "content_length": len(entry.content),
            }
            for entry in entries
        ],
    }


@router.get("/feeds/stats")
def get_feed_statistics(db: Session = Depends(get_db)):
    """
    Get aggregate statistics about feed ingestion.

    Returns totals and breakdowns by provider.
    """
    from ..models import Source, CompanyMention

    # Total sources by provider
    rss_sources = db.query(Source).filter(Source.provider == "rss").count()
    finnhub_sources = db.query(Source).filter(Source.provider == "finnhub").count()
    manual_sources = db.query(Source).filter(Source.provider == "manual").count()

    # Total mentions
    total_mentions = db.query(CompanyMention).count()

    # Unprocessed sources
    unprocessed = db.query(Source).filter(Source.processed == False).count()

    return {
        "sources_by_provider": {
            "rss": rss_sources,
            "finnhub": finnhub_sources,
            "manual": manual_sources,
            "total": rss_sources + finnhub_sources + manual_sources,
        },
        "total_mentions": total_mentions,
        "unprocessed_sources": unprocessed,
    }
