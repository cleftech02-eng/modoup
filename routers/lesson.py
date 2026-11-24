from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from model import Activity, Lesson, LessonCompletion, User
from schemes.lesson import CompleteOut, LessonOut
from services.progress_service import get_progress

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("", response_model=list[LessonOut])
def list_lessons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.current_realm_id is None:
        raise HTTPException(status_code=400, detail="Choose a realm first")

    lessons = (
        db.query(Lesson)
        .filter(Lesson.realm_id == current_user.current_realm_id)
        .order_by(Lesson.order_index)
        .all()
    )
    done_ids = {
        c.lesson_id
        for c in db.query(LessonCompletion).filter(
            LessonCompletion.user_id == current_user.id
        )
    }
    return [
        LessonOut(
            id=l.id,
            title=l.title,
            content=l.content,
            order_index=l.order_index,
            completed=l.id in done_ids,
        )
        for l in lessons
    ]


@router.post("/{lesson_id}/complete", response_model=CompleteOut)
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    already = (
        db.query(LessonCompletion)
        .filter(
            LessonCompletion.user_id == current_user.id,
            LessonCompletion.lesson_id == lesson_id,
        )
        .first()
    )
    if already:
        raise HTTPException(status_code=400, detail="Lesson already completed")

    db.add(LessonCompletion(user_id=current_user.id, lesson_id=lesson_id))
    db.add(Activity(
        user_id=current_user.id,
        type="lesson_completed",
        message=f"{current_user.full_name} completed '{lesson.title}'",
    ))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Lesson already completed")

    progress = get_progress(db, current_user.id)
    return CompleteOut(message="Lesson completed!", **progress)