from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("realm_id", "order_index", name="uq_lesson_realm_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150))
    content: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer)  # position within the realm

    realm_id: Mapped[int] = mapped_column(
        ForeignKey("realms.id", ondelete="CASCADE"), index=True
    )

    # Relationships
    realm: Mapped["Realm"] = relationship(back_populates="lessons")
    completions: Mapped[list["LessonCompletion"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )

    lessons: Mapped[list["Lesson"]] = relationship(
    back_populates="realm",
    order_by="Lesson.order_index",
    cascade="all, delete-orphan",
)