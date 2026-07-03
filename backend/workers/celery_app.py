"""
Celery application factory for CEO Tracker background tasks.

This module sets up the Celery app with Redis broker and backend.
"""
import os
from celery import Celery
from logging.config import dictConfig

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Configure logging
dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['default'],
        'level': 'INFO',
    },
})

# Create Celery app
celery_app = Celery(
    'ceo_tracker',
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Celery configuration
celery_app.conf.update(
    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task results
    result_expires=3600,  # 1 hour
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Task execution
    task_acks_late=True,  # Acknowledge after task completion
    worker_prefetch_multiplier=1,  # Prevent prefetching too many tasks

    # Rate limiting
    task_annotations={
        'workers.tasks.fetch_rss_feed': {'rate_limit': '10/m'},
        'workers.tasks.fetch_finnhub_news': {'rate_limit': '10/m'},
    },

    # Error handling
    task_reject_on_worker_lost=True,
)

# Auto-discover tasks in workers package
celery_app.autodiscover_tasks(['workers'])

# Import beat schedule
try:
    from workers.beat_config import beat_schedule
    celery_app.conf.beat_schedule = beat_schedule
except ImportError:
    # If beat_config doesn't exist yet, use empty schedule
    celery_app.conf.beat_schedule = {}

if __name__ == '__main__':
    celery_app.start()
