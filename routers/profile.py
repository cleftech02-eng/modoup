from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from model import Lesson, LessonCompletion, Realm, User
from schemes.profile import ProfileOut
from services.progress_service import get_progress

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=ProfileOut)
def my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    progress = get_progress(db, current_user.id)

    realm = None
    total = 0
    done = 0
    if current_user.current_realm_id is not None:
        realm = db.query(Realm).filter(
            Realm.id == current_user.current_realm_id
        ).first()
        total = (
            db.query(Lesson)
            .filter(Lesson.realm_id == current_user.current_realm_id)
            .count()
        )
        done = (
            db.query(LessonCompletion)
            .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
            .filter(
                LessonCompletion.user_id == current_user.id,
                Lesson.realm_id == current_user.current_realm_id,
            )
            .count()
        )

    percent = round(done / total * 100) if total else 0

    return ProfileOut(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        realm=realm,
        hp=progress["hp"],
        level=progress["level"],
        completed_lessons=progress["completed_lessons"],
        realm_total_lessons=total,
        realm_completed_lessons=done,
        realm_progress_percent=percent,
    )