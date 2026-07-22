from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, date
from pydantic import BaseModel

from database import get_db
from models import PeriodHistory, User
from auth import get_current_user

router = APIRouter(
    prefix="/period",
    tags=["Period Tracker"]
)


# -------------------------
# Request Schema
# -------------------------

class PeriodCreate(BaseModel):
    start_date: date
    period_length: int = 5
    cycle_length: int = 28


# -------------------------
# Add Period
# -------------------------

@router.post("/")
def add_period(
    data: PeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not (1 <= data.period_length <= 10):
        raise HTTPException(
            status_code=400,
            detail="Period length must be between 1 and 10 days"
        )

    if not (21 <= data.cycle_length <= 45):
        raise HTTPException(
            status_code=400,
            detail="Cycle length must be between 21 and 45 days"
        )

    end_date = data.start_date + timedelta(days=data.period_length - 1)

    history = PeriodHistory(
        user_id=current_user.id,
        start_date=data.start_date,
        end_date=end_date,
        period_length=data.period_length,
        cycle_length=data.cycle_length
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "message": "Period saved successfully",
        "period": {
            "id": history.id,
            "start_date": history.start_date.isoformat(),
            "end_date": history.end_date.isoformat()
        }
    }


# -------------------------
# Period History
# -------------------------

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    history = (
        db.query(PeriodHistory)
        .filter(PeriodHistory.user_id == current_user.id)
        .order_by(PeriodHistory.start_date.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "start_date": item.start_date.isoformat(),
            "end_date": item.end_date.isoformat(),
            "period_length": item.period_length,
            "cycle_length": item.cycle_length
        }
        for item in history
    ]


# -------------------------
# Calendar Prediction
# -------------------------

@router.get("/calendar")
def get_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    latest = (
        db.query(PeriodHistory)
        .filter(PeriodHistory.user_id == current_user.id)
        .order_by(PeriodHistory.start_date.desc())
        .first()
    )

    if not latest:
        return {
            "message": "No period data found"
        }

    next_period = latest.start_date + timedelta(days=latest.cycle_length)

    ovulation = next_period - timedelta(days=14)

    fertile_start = ovulation - timedelta(days=5)

    fertile_end = ovulation + timedelta(days=1)

    period_days = []

    current = latest.start_date

    while current <= latest.end_date:
        period_days.append(current.isoformat())
        current += timedelta(days=1)

    return {
        "last_period": latest.start_date.isoformat(),
        "next_period": next_period.isoformat(),
        "ovulation": ovulation.isoformat(),
        "fertile_window": {
            "start": fertile_start.isoformat(),
            "end": fertile_end.isoformat()
        },
        "period_days": period_days
    }