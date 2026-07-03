"""
Shared ingestion service for processing text through NLP pipeline.

This service provides a unified way to ingest text from various sources
(manual, RSS feeds, API) and process them through the NER and sentiment
analysis pipeline.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Company, Source, Speech, CompanyMention
from .ner import get_ner_service, KNOWN_COMPANIES
from .sentiment import get_sentiment_service

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service for ingesting and processing text through the NLP pipeline.

    Pipeline: Text → NER → Sentiment Analysis → Database
    """

    def __init__(self, db: Session):
        """
        Initialize the ingestion service.

        Args:
            db: Database session
        """
        self.db = db
        self.ner_service = get_ner_service()
        self.sentiment_service = get_sentiment_service()

    def process_text(
        self,
        text: str,
        source_url: Optional[str] = None,
        title: Optional[str] = None,
        ceo_id: Optional[int] = None,
        source_type: str = "manual",
        provider: str = "manual",
        published_at: Optional[datetime] = None,
    ) -> Dict:
        """
        Process text through the full NLP pipeline.

        Args:
            text: Text content to process
            source_url: URL of the source (optional)
            title: Title of the source (optional)
            ceo_id: ID of the CEO speaking (optional, required for speech creation)
            source_type: Type of source (manual, rss, api, etc.)
            provider: Data provider (manual, rss, finnhub, etc.)
            published_at: Publication date (optional)

        Returns:
            Dictionary with processing results including created records
        """
        if not text:
            return {
                "success": False,
                "message": "No text provided",
                "mentions_created": 0,
            }

        try:
            # Step 1: Create source record
            source = self._create_source(
                url=source_url,
                title=title,
                content=text,
                source_type=source_type,
                provider=provider,
                published_at=published_at,
            )

            # Step 2: Create speech record if CEO provided
            speech = None
            if ceo_id:
                speech = self._create_speech(source.id, ceo_id, text)

            # Step 3: Extract company mentions
            mentions = self.ner_service.extract_company_mentions(
                text=text,
                known_companies=KNOWN_COMPANIES,
            )

            # Step 4: Process mentions with sentiment analysis
            mentions_created = self._process_mentions(
                mentions=mentions,
                source=source,
                speech=speech,
            )

            # Step 5: Mark source as processed
            source.processed = True
            self.db.commit()

            logger.info(f"Processed text: {mentions_created} mentions created")

            return {
                "success": True,
                "message": f"Successfully processed text. Found {mentions_created} company mentions.",
                "mentions_created": mentions_created,
                "source_id": source.id,
                "speech_id": speech.id if speech else None,
            }

        except Exception as e:
            logger.error(f"Error processing text: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error processing text: {str(e)}",
                "mentions_created": 0,
            }

    def _create_source(
        self,
        url: Optional[str],
        title: Optional[str],
        content: str,
        source_type: str,
        provider: str,
        published_at: Optional[datetime],
    ) -> Source:
        """Create a new Source record."""
        source = Source(
            url=url,
            title=title,
            source_type=source_type,
            provider=provider,
            raw_text=content,
            published_at=published_at or datetime.utcnow(),
            processed=False,
        )
        self.db.add(source)
        self.db.flush()
        return source

    def _create_speech(self, source_id: int, ceo_id: int, quote_text: str) -> Speech:
        """Create a new Speech record."""
        speech = Speech(
            source_id=source_id,
            ceo_id=ceo_id,
            quote_text=quote_text,
            mentioned_at=datetime.utcnow(),
        )
        self.db.add(speech)
        self.db.flush()
        return speech

    def _process_mentions(
        self,
        mentions: List[Dict],
        source: Source,
        speech: Optional[Speech],
    ) -> int:
        """
        Process extracted mentions with sentiment analysis.

        Args:
            mentions: List of extracted company mentions
            source: Source record
            speech: Speech record (optional)

        Returns:
            Number of mentions created
        """
        mentions_created = 0

        for mention_data in mentions:
            try:
                # Find or create company
                company = self._get_or_create_company(
                    name=mention_data["company"],
                    ticker=mention_data["ticker"],
                )

                # Analyze sentiment for the context
                sentiment_result = self.sentiment_service.analyze_sentiment(
                    text=mention_data["context"]
                )

                # Create company mention
                # If we have a speech, link to it; otherwise link to source only
                company_mention = CompanyMention(
                    speech_id=speech.id if speech else None,
                    mentioned_company_id=company.id,
                    context_text=mention_data["context"],
                    sentiment=sentiment_result["sentiment"],
                    sentiment_confidence=sentiment_result["confidence"],
                )
                self.db.add(company_mention)
                mentions_created += 1

            except Exception as e:
                logger.error(f"Error processing mention: {e}")
                continue

        return mentions_created

    def _get_or_create_company(self, name: str, ticker: str) -> Company:
        """
        Get existing company or create a new one.

        Args:
            name: Company name
            ticker: Company ticker symbol

        Returns:
            Company record
        """
        # Try to find by name or ticker
        company = self.db.query(Company).filter(
            (Company.name == name) | (Company.ticker == ticker)
        ).first()

        if not company:
            company = Company(
                name=name,
                ticker=ticker,
                is_tracked=False,  # New companies are not tracked by default
            )
            self.db.add(company)
            self.db.flush()
            logger.info(f"Created new company: {name} ({ticker})")

        return company

    def process_rss_entry(
        self,
        entry: Dict,
        feed_config: Dict,
    ) -> Dict:
        """
        Process an RSS feed entry through the NLP pipeline.

        Args:
            entry: RSS entry dictionary with title, url, content, published_at
            feed_config: Feed configuration dictionary

        Returns:
            Processing result dictionary
        """
        # For RSS entries, we typically don't have a specific CEO speaking
        # The content is from the company itself (press release)
        # So we create a Source but not a Speech

        try:
            # Check if already exists
            from .feeds import get_feed_service
            feed_service = get_feed_service()

            if feed_service.is_duplicate(entry.get("url", ""), self.db):
                return {
                    "success": False,
                    "message": "Entry already exists",
                    "mentions_created": 0,
                    "duplicate": True,
                }

            # Create source without CEO (company press release)
            source = self._create_source(
                url=entry.get("url"),
                title=entry.get("title"),
                content=entry.get("content"),
                source_type="press_release",
                provider=feed_config.get("provider", "rss"),
                published_at=entry.get("published_at"),
            )

            # Extract mentions
            mentions = self.ner_service.extract_company_mentions(
                text=entry.get("content", ""),
                known_companies=KNOWN_COMPANIES,
            )

            # Process mentions (without speech)
            mentions_created = self._process_mentions(
                mentions=mentions,
                source=source,
                speech=None,  # RSS entries are press releases, not CEO speeches
            )

            # Mark as processed
            source.processed = True
            self.db.commit()

            return {
                "success": True,
                "message": f"Processed RSS entry: {mentions_created} mentions",
                "mentions_created": mentions_created,
                "source_id": source.id,
                "duplicate": False,
            }

        except Exception as e:
            logger.error(f"Error processing RSS entry: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "mentions_created": 0,
                "duplicate": False,
            }

    def get_ingestion_stats(self) -> Dict:
        """Get ingestion statistics."""
        total_sources = self.db.query(Source).count()
        processed_sources = self.db.query(Source).filter(Source.processed.is_(True)).count()
        total_mentions = self.db.query(CompanyMention).count()

        return {
            "total_sources": total_sources,
            "processed_sources": processed_sources,
            "total_mentions": total_mentions,
            "processing_rate": f"{processed_sources / total_sources * 100:.1f}%" if total_sources > 0 else "0%",
        }
