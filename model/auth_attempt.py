
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class AuthAttempt(Base):
    __tablename__ = "auth_attempts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    identifier: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    window_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    blocked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "action",
            "identifier",
            name="uq_auth_attempt_action_identifier",
        ),
    )
