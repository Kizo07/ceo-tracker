"""
API endpoints for CEOs.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..db.database import get_db
from ..models import CEO, Company

router = APIRouter()


class CEOResponse(BaseModel):
    """Response model for a CEO."""
    id: int
    name: str
    company_id: int
    company_name: str
    company_ticker: str
    title: str | None
    twitter_handle: str | None

    class Config:
        from_attributes = True


@router.get("/ceos", response_model=List[CEOResponse])
def get_ceos(db: Session = Depends(get_db)):
    """Get list of all tracked CEOs."""
    ceos = db.query(CEO).order_by(CEO.name).all()

    responses = []
    for ceo in ceos:
        company = db.query(Company).filter(Company.id == ceo.company_id).first()
        responses.append(CEOResponse(
            id=ceo.id,
            name=ceo.name,
            company_id=ceo.company_id,
            company_name=company.name if company else "",
            company_ticker=company.ticker if company else "",
            title=ceo.title,
            twitter_handle=ceo.twitter_handle,
        ))

    return responses


@router.get("/ceos/{ceo_id}", response_model=CEOResponse)
def get_ceo(ceo_id: int, db: Session = Depends(get_db)):
    """Get details of a specific CEO."""
    ceo = db.query(CEO).filter(CEO.id == ceo_id).first()
    if not ceo:
        raise HTTPException(status_code=404, detail="CEO not found")

    company = db.query(Company).filter(Company.id == ceo.company_id).first()

    return CEOResponse(
        id=ceo.id,
        name=ceo.name,
        company_id=ceo.company_id,
        company_name=company.name if company else "",
        company_ticker=company.ticker if company else "",
        title=ceo.title,
        twitter_handle=ceo.twitter_handle,
    )
