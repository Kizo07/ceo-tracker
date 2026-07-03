"""
SQLAlchemy models for CEO Tracker database.
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from ..db.database import Base
from datetime import datetime


class Company(Base):
    """Company model representing tracked and mentioned companies."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, nullable=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    is_tracked = Column(Boolean, default=True, index=True)  # If in top 20
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    ceos = relationship("CEO", back_populates="company")
    mentions_received = relationship("CompanyMention", foreign_keys="CompanyMention.mentioned_company_id", back_populates="mentioned_company")


class CEO(Base):
    """CEO model representing tracked executives."""
    __tablename__ = "ceos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(100), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="ceos")
    speeches = relationship("Speech", back_populates="ceo")


class Source(Base):
    """Source model for articles, transcripts, and press releases."""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, unique=True, nullable=True)
    title = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=True, index=True)
    provider = Column(String(100), nullable=True)  # 'finnhub', 'seeking_alpha', etc.
    published_at = Column(DateTime, nullable=True, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    raw_text = Column(Text, nullable=True)
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    speeches = relationship("Speech", back_populates="source")


class Speech(Base):
    """Speech model for CEO quotes and commentary."""
    __tablename__ = "speeches"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    ceo_id = Column(Integer, ForeignKey("ceos.id"), nullable=False)
    quote_text = Column(Text, nullable=False)
    mentioned_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    source = relationship("Source", back_populates="speeches")
    ceo = relationship("CEO", back_populates="speeches")
    mentions = relationship("CompanyMention", back_populates="speech")


class CompanyMention(Base):
    """CompanyMention model for tracking when a CEO mentions another company."""
    __tablename__ = "company_mentions"

    id = Column(Integer, primary_key=True, index=True)
    speech_id = Column(Integer, ForeignKey("speeches.id"), nullable=True)
    mentioned_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    context_text = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=True, index=True)  # 'positive', 'negative', 'neutral'
    sentiment_confidence = Column(Float, nullable=True)
    relationship_type = Column(String(50), nullable=True)  # 'competitor', 'partner', etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    speech = relationship("Speech", back_populates="mentions")
    mentioned_company = relationship("Company", foreign_keys=[mentioned_company_id], back_populates="mentions_received")
