from sqlalchemy.orm import Session

from model import LessonCompletion

HP_PER_LESSON = 10
HP_PER_LEVEL = 100


def get_progress(db: Session, user_id: int) -> dict:
    completed = (
        db.query(LessonCompletion)
        .filter(LessonCompletion.user_id == user_id)
        .count()
    )
    hp = completed * HP_PER_LESSON
    level = 1 + hp // HP_PER_LEVEL
    return {"completed_lessons": completed, "hp": hp, "level": level}