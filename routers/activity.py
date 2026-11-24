from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from model import Activity, User
from schemes.activity import ActivityOut

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get("", response_model=list[ActivityOut])
def activity_feed(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Activity)
        .order_by(Activity.created_at.desc(), Activity.id.desc())
        .limit(limit)
        .all()
    )