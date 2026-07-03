"""
Celery Beat schedule configuration for CEO Tracker.

Defines periodic tasks for RSS feed polling and data ingestion.
"""
from celery.schedules import crontab

# Feed configuration
FEEDS_CONFIG = {
    'apple': {'url': 'https://www.apple.com/newsroom/rss-feed.rss', 'company_id': 1},
    'microsoft': {'url': 'https://news.microsoft.com/feed/', 'company_id': 2},
    'nvidia': {'url': 'https://nvidianews.nvidia.com/rss.xml', 'company_id': 3},
    'alphabet': {'url': 'https://blog.google/rss/', 'company_id': 4},
    'amazon': {'url': 'https://www.aboutamazon.com/news/rss', 'company_id': 5},
}

# Celery Beat schedule
beat_schedule = {
    # Poll each RSS feed every 4 hours
    'fetch-apple-rss': {
        'task': 'workers.tasks.fetch_rss_feed',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at :00
        'args': ['apple'],
    },
    'fetch-microsoft-rss': {
        'task': 'workers.tasks.fetch_rss_feed',
        'schedule': crontab(minute=15, hour='*/4'),  # Every 4 hours at :15
        'args': ['microsoft'],
    },
    'fetch-nvidia-rss': {
        'task': 'workers.tasks.fetch_rss_feed',
        'schedule': crontab(minute=30, hour='*/4'),  # Every 4 hours at :30
        'args': ['nvidia'],
    },
    'fetch-alphabet-rss': {
        'task': 'workers.tasks.fetch_rss_feed',
        'schedule': crontab(minute=45, hour='*/4'),  # Every 4 hours at :45
        'args': ['alphabet'],
    },
    'fetch-amazon-rss': {
        'task': 'workers.tasks.fetch_rss_feed',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at :00
        'args': ['amazon'],
    },

    # Optional: Finnhub news polling (if API key is configured)
    # 'fetch-finnhub-news': {
    #     'task': 'workers.tasks.fetch_finnhub_news',
    #     'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    #     'args': [['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN']],
    # },

    # Cleanup old sources (runs daily at midnight)
    'cleanup-old-sources': {
        'task': 'workers.tasks.cleanup_old_sources',
        'schedule': crontab(minute=0, hour=0),  # Daily at midnight
        'args': [30],  # Keep sources for 30 days
    },
}
