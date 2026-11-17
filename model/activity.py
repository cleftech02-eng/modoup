from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(50))          # e.g. "lesson_completed"
    message: Mapped[str] = mapped_column(Text)             # e.g. "Ada completed Frontend Lesson 2"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    
    user = relationship("User", back_populates="activities")