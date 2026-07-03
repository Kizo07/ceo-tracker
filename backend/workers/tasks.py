"""
Celery tasks for CEO Tracker background processing.

Tasks include RSS feed fetching, Finnhub API calls, and data cleanup.
"""
from datetime import datetime, timedelta
from typing import Dict, List

from celery import shared_task
from celery.utils.log import get_task_logger

from workers.celery_app import celery_app
from app.services.feeds import get_feed_service
from app.services.ingestion import IngestionService
from app.services.finnhub import get_finnhub_service
from app.db.database import SessionLocal

logger = get_task_logger(__name__)


@celery_app.task(name='workers.tasks.fetch_rss_feed')
def fetch_rss_feed(feed_key: str) -> Dict:
    """
    Fetch and process a single RSS feed.

    Args:
        feed_key: Key of the feed in feeds.yaml (e.g., 'apple', 'microsoft')

    Returns:
        Dictionary with processing results
    """
    logger.info(f"Starting RSS feed fetch for: {feed_key}")

    db = SessionLocal()
    try:
        # Get feed service and configuration
        feed_service = get_feed_service()
        feed_config = feed_service.get_feed(feed_key)

        if not feed_config:
            logger.error(f"Feed not found: {feed_key}")
            return {
                "success": False,
                "message": f"Feed not found: {feed_key}",
                "entries_processed": 0,
                "mentions_created": 0,
            }

        # Fetch the RSS feed
        entries = feed_service.fetch_feed(feed_config.url)

        if not entries:
            logger.warning(f"No entries fetched from {feed_key}")
            return {
                "success": True,
                "message": "No new entries",
                "entries_processed": 0,
                "mentions_created": 0,
            }

        # Process each entry
        ingestion_service = IngestionService(db)
        entries_processed = 0
        mentions_created = 0
        duplicates = 0

        for entry in entries:
            # Check for duplicate
            if feed_service.is_duplicate(entry.url, db):
                duplicates += 1
                continue

            # Process the entry
            result = ingestion_service.process_rss_entry(
                entry={
                    "title": entry.title,
                    "url": entry.url,
                    "content": entry.content,
                    "published_at": entry.published_at,
                },
                feed_config={
                    "provider": feed_config.provider,
                    "company_id": feed_config.company_id,
                },
            )

            if result.get("success"):
                entries_processed += 1
                mentions_created += result.get("mentions_created", 0)

        logger.info(
            f"Feed {feed_key}: {entries_processed} processed, "
            f"{mentions_created} mentions, {duplicates} duplicates"
        )

        return {
            "success": True,
            "message": f"Processed {entries_processed} entries from {feed_key}",
            "entries_processed": entries_processed,
            "mentions_created": mentions_created,
            "duplicates": duplicates,
            "feed_key": feed_key,
        }

    except Exception as e:
        logger.error(f"Error processing feed {feed_key}: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "entries_processed": 0,
            "mentions_created": 0,
        }
    finally:
        db.close()


@celery_app.task(name='workers.tasks.fetch_all_feeds')
def fetch_all_feeds() -> Dict:
    """
    Fetch and process all configured RSS feeds.

    Returns:
        Dictionary with aggregate results
    """
    logger.info("Starting fetch for all RSS feeds")

    feed_service = get_feed_service()
    feeds = feed_service.get_feeds()

    results = {}
    total_entries = 0
    total_mentions = 0

    # Call fetch_rss_feed directly (synchronously within this task)
    for feed_key in feeds.keys():
        result = fetch_rss_feed(feed_key)
        results[feed_key] = result
        total_entries += result.get("entries_processed", 0)
        total_mentions += result.get("mentions_created", 0)

    logger.info(f"All feeds complete: {total_entries} entries, {total_mentions} mentions")

    return {
        "success": True,
        "message": f"Processed {len(feeds)} feeds",
        "total_entries": total_entries,
        "total_mentions": total_mentions,
        "results": results,
    }


@celery_app.task(name='workers.tasks.fetch_finnhub_news')
def fetch_finnhub_news(symbols: List[str]) -> Dict:
    """
    Fetch news from Finnhub API for given symbols.

    Args:
        symbols: List of stock symbols (e.g., ['AAPL', 'MSFT'])

    Returns:
        Dictionary with processing results
    """
    logger.info(f"Fetching Finnhub news for: {symbols}")

    # Check if API key is configured
    import os
    if not os.getenv("FINNHUB_API_KEY"):
        logger.warning("Finnhub API key not configured, skipping")
        return {
            "success": False,
            "message": "Finnhub API key not configured",
            "articles_processed": 0,
        }

    db = SessionLocal()
    try:
        finnhub_service = get_finnhub_service()
        ingestion_service = IngestionService(db)

        total_articles = 0
        total_mentions = 0

        for symbol in symbols:
            # Get news from Finnhub
            news_items = finnhub_service.get_company_news(symbol)

            for item in news_items:
                # Parse the news item
                parsed = finnhub_service.parse_news_item(item)

                # Check for duplicate
                feed_service = get_feed_service()
                if feed_service.is_duplicate(parsed["url"], db):
                    continue

                # Process the entry
                result = ingestion_service.process_rss_entry(
                    entry={
                        "title": parsed["title"],
                        "url": parsed["url"],
                        "content": parsed["content"],
                        "published_at": parsed["published_at"],
                    },
                    feed_config={
                        "provider": "finnhub",
                        "company_id": None,  # Will be determined by content
                    },
                )

                if result.get("success"):
                    total_articles += 1
                    total_mentions += result.get("mentions_created", 0)

        logger.info(f"Finnhub: {total_articles} articles, {total_mentions} mentions")

        return {
            "success": True,
            "message": f"Processed {total_articles} articles from Finnhub",
            "articles_processed": total_articles,
            "mentions_created": total_mentions,
        }

    except Exception as e:
        logger.error(f"Error fetching Finnhub news: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "articles_processed": 0,
        }
    finally:
        db.close()


@celery_app.task(name='workers.tasks.cleanup_old_sources')
def cleanup_old_sources(days_to_keep: int = 30) -> Dict:
    """
    Clean up old source records from the database.

    Args:
        days_to_keep: Number of days of history to keep

    Returns:
        Dictionary with cleanup results
    """
    logger.info(f"Starting cleanup: keeping {days_to_keep} days of data")

    db = SessionLocal()
    try:
        from app.models import Source

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Count old sources
        old_sources = db.query(Source).filter(
            Source.published_at < cutoff_date
        ).count()

        if old_sources == 0:
            return {
                "success": True,
                "message": "No old sources to clean up",
                "sources_deleted": 0,
            }

        # Delete old sources (cascade should handle related records)
        db.query(Source).filter(
            Source.published_at < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Cleanup complete: {old_sources} sources deleted")

        return {
            "success": True,
            "message": f"Deleted {old_sources} old sources",
            "sources_deleted": old_sources,
        }

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "sources_deleted": 0,
        }
    finally:
        db.close()


@shared_task(name='workers.tasks.test_task')
def test_task() -> Dict:
    """
    Simple test task to verify Celery is working.

    Returns:
        Dictionary with test results
    """
    logger.info("Test task executed successfully")
    return {
        "success": True,
        "message": "Test task completed",
        "timestamp": datetime.utcnow().isoformat(),
    }
