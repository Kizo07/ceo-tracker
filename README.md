# CEO Tracker

A self-hosted web application that tracks CEO speeches and news from the top US firms by market cap, extracting mentions of other companies with sentiment analysis.

## Features

- **Company Mention Extraction**: Automatically identifies when CEOs mention other companies
- **Sentiment Analysis**: Determines if mentions are positive, negative, or neutral
- **CEO Tracking**: Focuses on top 5 companies (Apple, Microsoft, NVIDIA, Alphabet, Amazon) for MVP
- **Dashboard View**: Visualize mentions, sentiment distribution, and activity

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React
- **Database**: PostgreSQL
- **Queue**: Redis + Celery (for async processing)
- **NLP**: spaCy (NER) + FinBERT (sentiment analysis)
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- (Optional) Finnhub API key for press release data

### Running with Docker Compose

```bash
# Clone and navigate to project
cd ceo-tracker

# Start all services
docker-compose up -d

# Initialize database with companies and CEOs
docker-compose exec backend python init_db.py

# Access the application
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000 (when implemented)
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start PostgreSQL (or use Docker)
docker run -d \
  --name ceo_tracker_postgres \
  -e POSTGRES_USER=ceo_tracker \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ceo_tracker \
  -p 5432:5432 \
  postgres:16-alpine

# Initialize database
python init_db.py

# Run the application
uvicorn app.main:app --reload
```

## API Endpoints

### Mentions
- `GET /api/mentions` - Get paginated list of mentions
- `GET /api/mentions/ceo/{ceo_id}` - Get mentions by specific CEO
- `GET /api/mentions/company/{ticker}` - Get who mentioned a company
- `GET /api/sentiment/summary/{ceo_id}` - Sentiment breakdown per CEO

### CEOs & Companies
- `GET /api/ceos` - Get all tracked CEOs
- `GET /api/companies` - Get all companies
- `GET /api/companies/ticker/{ticker}` - Get company by ticker

### Dashboard
- `GET /api/dashboard` - Get overall statistics
- `GET /api/timeline` - Get chronological feed of mentions

### Ingestion
- `POST /api/ingest` - Manually submit text for analysis
- `POST /api/ingest/test` - Test with sample text
- `GET /api/ingest/status` - Get ingestion statistics

## Tracked Companies (MVP)

| Company | Ticker | CEO |
|---------|--------|-----|
| Apple | AAPL | Tim Cook |
| Microsoft | MSFT | Satya Nadella |
| NVIDIA | NVDA | Jensen Huang |
| Alphabet | GOOGL | Sundar Pichai |
| Amazon | AMZN | Andy Jassy |

## Project Structure

```
ceo-tracker/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # NLP services (NER, sentiment)
│   │   ├── db/           # Database configuration
│   │   └── main.py       # FastAPI app entry
│   ├── workers/          # Celery tasks (coming soon)
│   ├── init_db.py        # Database initialization
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/              # React app (coming soon)
├── docker-compose.yml
└── README.md
```

## Development Roadmap

### Phase 1: Core Pipeline ✅
- [x] FastAPI backend setup
- [x] PostgreSQL database schema
- [x] NER module (spaCy)
- [x] Sentiment analysis (FinBERT)
- [x] REST API endpoints

### Phase 2: Press Release Ingestion (Next)
- [ ] RSS feed reader for company investor relations
- [ ] Finnhub Press Releases API integration
- [ ] Celery workers for async processing

### Phase 3: React UI
- [ ] Dashboard with recent mentions
- [ ] CEO detail pages
- [ ] Sentiment visualization

### Phase 4: Enhancement & Scale
- [ ] Earnings transcripts integration
- [ ] Expand to top 20 companies
- [ ] Relationship detection
- [ ] Timeline view

## Contributing

This is a personal project for tracking CEO mentions. Contributions welcome!

## License

MIT
