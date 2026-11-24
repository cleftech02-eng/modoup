from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.user import User
    from model.lesson import Lesson

class Realm(Base):
    __tablename__ = "realms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(50), unique=True)  # e.g. "frontend", "backend"

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="current_realm")
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="realm", order_by="Lesson.order_index")