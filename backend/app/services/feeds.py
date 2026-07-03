"""
RSS Feed service for fetching and parsing company press releases.
"""
import feedparser
import logging
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from pathlib import Path
import yaml

from ..models import Source

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


@dataclass
class FeedEntry:
    """Represents a parsed RSS feed entry."""
    title: str
    url: str
    published_at: Optional[datetime]
    content: str
    author: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class FeedConfig:
    """Configuration for a single RSS feed."""
    name: str
    ticker: str
    url: str
    company_id: int
    provider: str = "rss"
    description: str = ""


class FeedService:
    """
    Service for fetching and parsing RSS feeds from company investor relations pages.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the FeedService.

        Args:
            config_path: Path to the feeds.yaml configuration file
        """
        self.config_path = config_path or self._get_default_config_path()
        self.feeds_config: Dict[str, FeedConfig] = {}
        self.schedule_config: Dict[str, Any] = {}
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the default path to feeds.yaml."""
        # Try multiple possible locations
        possible_paths = [
            "config/feeds.yaml",
            "app/config/feeds.yaml",
            "/home/fire/ceo-tracker/backend/config/feeds.yaml",
        ]
        for path in possible_paths:
            if Path(path).exists():
                return path
        return "config/feeds.yaml"

    def _load_config(self) -> None:
        """Load feed configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Load feed configurations
            if 'feeds' in config:
                for feed_key, feed_data in config['feeds'].items():
                    self.feeds_config[feed_key] = FeedConfig(**feed_data)

            # Load schedule configuration
            self.schedule_config = config.get('schedule', {})

            logger.info(f"Loaded {len(self.feeds_config)} feed configurations")

        except FileNotFoundError:
            logger.warning(f"Feed config file not found: {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading feed config: {e}")

    def get_feeds(self) -> Dict[str, FeedConfig]:
        """Get all configured feeds."""
        return self.feeds_config

    def get_feed(self, feed_key: str) -> Optional[FeedConfig]:
        """Get a specific feed configuration by key."""
        return self.feeds_config.get(feed_key)

    def fetch_feed(self, feed_url: str, max_entries: int = 50) -> List[FeedEntry]:
        """
        Fetch and parse an RSS feed.

        Args:
            feed_url: URL of the RSS feed
            max_entries: Maximum number of entries to return

        Returns:
            List of FeedEntry objects
        """
        try:
            logger.info(f"Fetching RSS feed: {feed_url}")

            # Fetch the feed with proper User-Agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse the feed content
            feed = feedparser.parse(response.content)

            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")

            entries = []
            now = datetime.utcnow()

            # Get lookback days from schedule config
            lookback_days = self.schedule_config.get('lookback_days', 7)
            cutoff_date = now - timedelta(days=lookback_days)

            for entry in feed.entries[:max_entries]:
                try:
                    feed_entry = self._parse_entry(entry, cutoff_date)
                    if feed_entry:
                        entries.append(feed_entry)
                except Exception as e:
                    logger.error(f"Error parsing entry: {e}")
                    continue

            logger.info(f"Fetched {len(entries)} valid entries from {feed_url}")
            return entries

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            return []

    def _parse_entry(self, entry: Any, cutoff_date: datetime) -> Optional[FeedEntry]:
        """
        Parse a single feedparser entry into a FeedEntry.

        Args:
            entry: feedparser entry object
            cutoff_date: Minimum publication date for valid entries

        Returns:
            FeedEntry or None if entry is too old or invalid
        """
        # Extract basic fields
        title = entry.get('title', 'No Title')
        url = entry.get('link', '')

        if not url:
            return None

        # Extract publication date
        published_at = self._extract_published_date(entry)

        # Skip if too old
        if published_at and published_at < cutoff_date:
            return None

        # Extract content
        content = self._extract_content(entry)

        # Extract author
        author = entry.get('author', '')

        # Extract summary/description
        summary = entry.get('summary', '')

        # Extract tags
        tags = []
        if 'tags' in entry:
            tags = [tag.get('term', '') for tag in entry.tags if isinstance(tag, dict)]

        return FeedEntry(
            title=title,
            url=url,
            published_at=published_at,
            content=content,
            author=author,
            summary=summary,
            tags=tags
        )

    def _extract_published_date(self, entry: Any) -> Optional[datetime]:
        """
        Extract publication date from a feed entry.

        Handles multiple date field formats used by different RSS feeds.
        """
        # Try various date fields in order of preference
        date_fields = ['published_parsed', 'updated_parsed']

        for field in date_fields:
            if field in entry and entry[field]:
                try:
                    time_struct = entry[field]
                    return datetime(*time_struct[:6])
                except (TypeError, ValueError):
                    continue

        return None

    def _extract_content(self, entry: Any) -> str:
        """
        Extract text content from a feed entry.

        Handles multiple content formats used by different RSS feeds.
        """
        # Try content field first (some feeds use this)
        if 'content' in entry and entry['content']:
            content_list = entry['content']
            if isinstance(content_list, list) and len(content_list) > 0:
                content = content_list[0]
                if isinstance(content, dict):
                    value = content.get('value', '')
                    # Strip HTML tags if present
                    return self._strip_html(value)

        # Try summary/description
        for field in ['summary', 'description']:
            if field in entry and entry[field]:
                return self._strip_html(entry[field])

        # Fallback to title if no content found
        return entry.get('title', '')

    def _strip_html(self, text: str) -> str:
        """
        Strip HTML tags from text, keeping only the text content.

        This is a simple implementation that handles basic HTML.
        For production, consider using BeautifulSoup or similar.
        """
        # Simple HTML tag removal
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove HTML entities
        text = re.sub(r'&[a-z]+;', ' ', text)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text.strip()

    def is_duplicate(self, url: str, db: Session) -> bool:
        """
        Check if a source with this URL already exists.

        Args:
            url: URL to check
            db: Database session

        Returns:
            True if URL already exists in database
        """
        try:
            existing = db.query(Source).filter(Source.url == url).first()
            return existing is not None
        except Exception as e:
            logger.error(f"Error checking for duplicate: {e}")
            return False

    def get_feed_for_company(self, ticker: str) -> Optional[FeedConfig]:
        """
        Get the RSS feed configuration for a specific company ticker.

        Args:
            ticker: Company ticker symbol

        Returns:
            FeedConfig or None if not found
        """
        for feed_config in self.feeds_config.values():
            if feed_config.ticker == ticker:
                return feed_config
        return None

    def get_all_feed_urls(self) -> List[str]:
        """Get all configured feed URLs."""
        return [feed.url for feed in self.feeds_config.values()]


# Singleton instance
_feed_service: Optional[FeedService] = None


def get_feed_service() -> FeedService:
    """Get or create the singleton FeedService instance."""
    global _feed_service
    if _feed_service is None:
        _feed_service = FeedService()
    return _feed_service
