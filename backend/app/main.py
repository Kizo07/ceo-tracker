"""
FastAPI application for CEO Tracker.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .db.database import engine, get_db, init_db
from . import models


# Create FastAPI app
app = FastAPI(
    title="CEO Tracker",
    description="Track CEO speeches and news for company mentions and sentiment",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("Database initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down...")


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "app": "CEO Tracker",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "mentions": "/api/mentions",
            "dashboard": "/api/dashboard",
            "ceos": "/api/ceos",
            "companies": "/api/companies",
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import routers
from .api import mentions, ceos, companies, dashboard, ingest, feeds

# Include routers
app.include_router(mentions.router, prefix="/api", tags=["mentions"])
app.include_router(ceos.router, prefix="/api", tags=["ceos"])
app.include_router(companies.router, prefix="/api", tags=["companies"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(feeds.router, prefix="/api", tags=["feeds"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
