"""
Finnhub API service for fetching company press releases and news.

Note: Press releases may be a premium feature on Finnhub.
This service is structured to be extended once API access is confirmed.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import httpx
import os

logger = logging.getLogger(__name__)


class FinnhubService:
    """
    Service for interacting with the Finnhub API.

    Finnhub provides various endpoints for stock data, news, and press releases.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    # API rate limits: Free tier = 60 calls/minute
    RATE_LIMIT_DELAY = 1.0  # Seconds between calls to be safe

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Finnhub service.

        Args:
            api_key: Finnhub API key. If not provided, looks for FINNHUB_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            logger.warning("No Finnhub API key provided. Set FINNHUB_API_KEY environment variable.")

        self.client = httpx.Client(timeout=30.0)
        self.last_call_time = None

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Make a rate-limited API request.

        Args:
            endpoint: API endpoint path (e.g., "/news")
            params: Query parameters

        Returns:
            JSON response or None if error
        """
        if not self.api_key:
            logger.error("Cannot make request: No API key configured")
            return None

        try:
            # Add API key to params
            params["token"] = self.api_key

            # Simple rate limiting
            import time
            if self.last_call_time:
                elapsed = time.time() - self.last_call_time
                if elapsed < self.RATE_LIMIT_DELAY:
                    time.sleep(self.RATE_LIMIT_DELAY - elapsed)

            # Make request
            url = f"{self.BASE_URL}{endpoint}"
            response = self.client.get(url, params=params)
            response.raise_for_status()

            self.last_call_time = time.time()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def get_company_news(
        self,
        symbol: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Get company news and press releases.

        This endpoint provides general news which may include press releases.
        For dedicated press releases, a premium tier may be required.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            from_date: Start date (default: 30 days ago)
            to_date: End date (default: today)

        Returns:
            List of news items
        """
        if not self.api_key:
            logger.warning("Cannot fetch news: No API key configured")
            return []

        # Default date range: last 30 days
        if not from_date:
            from_date = date.today() - timedelta(days=30)
        if not to_date:
            to_date = date.today()

        params = {
            "symbol": symbol,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        result = self._make_request("/news", params)

        if result is None:
            return []

        if isinstance(result, dict) and "error" in result:
            logger.error(f"API error: {result['error']}")
            return []

        return result if isinstance(result, list) else []

    def get_press_releases(
        self,
        symbol: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Get company press releases (if available with your API tier).

        Note: This endpoint may require a premium subscription.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            from_date: Start date
            to_date: End date

        Returns:
            List of press release items
        """
        if not self.api_key:
            logger.warning("Cannot fetch press releases: No API key configured")
            return []

        # Try the press releases endpoint if available
        # Note: This endpoint may not be available on free tier
        if not from_date:
            from_date = date.today() - timedelta(days=30)
        if not to_date:
            to_date = date.today()

        params = {
            "symbol": symbol,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        # Try press releases endpoint first
        result = self._make_request("/press-releases", params)

        if result:
            return result if isinstance(result, list) else []

        # Fallback: Use company news and filter for press releases
        logger.info(f"Press releases endpoint not available, filtering company news for {symbol}")
        news_items = self.get_company_news(symbol, from_date, to_date)

        # Filter for press release-like items
        press_releases = [
            item for item in news_items
            if self._is_press_release(item)
        ]

        return press_releases

    def _is_press_release(self, news_item: Dict) -> bool:
        """
        Determine if a news item is likely a press release.

        Args:
            news_item: News item dictionary

        Returns:
            True if item appears to be a press release
        """
        # Check for press release indicators
        headline = news_item.get("headline", "").lower()
        source = news_item.get("source", "").lower()

        pr_indicators = ["press release", "pr:", "newsroom", "announcement"]
        pr_sources = ["newsroom", "press", "investor"]

        return (
            any(indicator in headline for indicator in pr_indicators) or
            any(indicator in source for indicator in pr_sources)
        )

    def parse_news_item(self, item: Dict) -> Dict:
        """
        Parse a Finnhub news item into a standard format.

        Args:
            item: Raw news item from Finnhub API

        Returns:
            Parsed item with standardized fields
        """
        return {
            "title": item.get("headline", ""),
            "url": item.get("url", ""),
            "published_at": datetime.fromtimestamp(item.get("datetime", 0)),
            "content": item.get("summary", ""),
            "source": item.get("source", "finnhub"),
            "symbols": item.get("related", []),
            "image": item.get("image", ""),
        }

    def close(self):
        """Close the HTTP client."""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Singleton instance
_finnhub_service: Optional[FinnhubService] = None


def get_finnhub_service() -> FinnhubService:
    """Get or create the singleton Finnhub service instance."""
    global _finnhub_service
    if _finnhub_service is None:
        _finnhub_service = FinnhubService()
    return _finnhub_service
