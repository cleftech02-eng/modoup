
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Email verification
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Google authentication
    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    auth_provider: Mapped[str] = mapped_column(
        String(20),
        default="local",
        nullable=False,
    )

    current_realm_id: Mapped[int | None] = mapped_column(
        ForeignKey("realms.id"),
        nullable=True,
    )

    hp: Mapped[int] = mapped_column(
        Integer,
        default=100,
    )

    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Relationships
    current_realm = relationship(
        "Realm",
        back_populates="users",
    )

    completions = relationship(
        "LessonCompletion",
        back_populates="user",
    )

    activities = relationship(
        "Activity",
        back_populates="user",
    )
