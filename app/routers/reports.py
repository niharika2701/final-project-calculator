import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import get_current_user
from app.schemas import ReportRead, CalculationRead
from app.report_service import compute_report_stats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=ReportRead)
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Return usage statistics for the currently authenticated user.

    Stats include:
    - total_calculations: how many calculations they have run
    - by_operation: count per operation type (Add, Sub, etc.)
    - average_a / average_b / average_result: mean values
    - most_recent: up to 5 most recently created calculations
    """
    logger.info(f"Report requested by user '{current_user.username}'")

    calcs = (
        db.query(models.Calculation)
        .filter(models.Calculation.user_id == current_user.id)
        .order_by(models.Calculation.created_at.desc())
        .all()
    )

    stats = compute_report_stats(calcs)
    most_recent = [CalculationRead.model_validate(c) for c in calcs[:5]]

    return ReportRead(**stats, most_recent=most_recent)