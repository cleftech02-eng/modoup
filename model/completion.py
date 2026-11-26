from sqlalchemy import ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base


class LessonCompletion(Base):
    __tablename__ = "lesson_completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # Prevent the same user from completing the same lesson twice
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="unique_user_lesson"),
    )

    # Relationships
    user = relationship("User", back_populates="completions")
    lesson = relationship("Lesson", back_populates="completions")