from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencied import get_db
from app.services.analytics import (
    AnalyticsSummary,
    get_analytics_summary,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)):
    return get_analytics_summary(db)