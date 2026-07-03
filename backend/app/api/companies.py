"""
API endpoints for companies.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..db.database import get_db
from ..models import Company

router = APIRouter()


class CompanyResponse(BaseModel):
    """Response model for a company."""
    id: int
    ticker: str | None
    name: str
    is_tracked: bool
    sector: str | None
    industry: str | None

    class Config:
        from_attributes = True


@router.get("/companies", response_model=List[CompanyResponse])
def get_companies(is_tracked: bool = None, db: Session = Depends(get_db)):
    """Get list of all companies."""
    query = db.query(Company)

    if is_tracked is not None:
        query = query.filter(Company.is_tracked == is_tracked)

    companies = query.order_by(Company.name).all()

    return [
        CompanyResponse(
            id=c.id,
            ticker=c.ticker,
            name=c.name,
            is_tracked=c.is_tracked,
            sector=c.sector,
            industry=c.industry,
        )
        for c in companies
    ]


@router.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get details of a specific company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse(
        id=company.id,
        ticker=company.ticker,
        name=company.name,
        is_tracked=company.is_tracked,
        sector=company.sector,
        industry=company.industry,
    )


@router.get("/companies/ticker/{ticker}", response_model=CompanyResponse)
def get_company_by_ticker(ticker: str, db: Session = Depends(get_db)):
    """Get a company by its ticker symbol."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")

    return CompanyResponse(
        id=company.id,
        ticker=company.ticker,
        name=company.name,
        is_tracked=company.is_tracked,
        sector=company.sector,
        industry=company.industry,
    )
