from datetime import datetime, timedelta, timezone
import hashlib

from sqlalchemy.orm import Session

from model.auth_attempt import AuthAttempt


MAX_ATTEMPTS = 5
LOCKOUT_HOURS = 12


def hash_identifier(value: str) -> str:
    return hashlib.sha256(
        value.strip().lower().encode("utf-8")
    ).hexdigest()


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def get_attempt_record(
    db: Session,
    action: str,
    identifier: str,
) -> AuthAttempt | None:
    hashed_identifier = hash_identifier(identifier)

    return (
        db.query(AuthAttempt)
        .filter(
            AuthAttempt.action == action,
            AuthAttempt.identifier == hashed_identifier,
        )
        .first()
    )


def check_rate_limit(
    db: Session,
    action: str,
    identifier: str,
) -> tuple[bool, int]:
    record = get_attempt_record(
        db,
        action,
        identifier,
    )

    if record is None:
        return True, 0

    now = get_utc_now()

    if record.blocked_until is None:
        return True, 0

    blocked_until = normalize_datetime(
        record.blocked_until
    )

    if now < blocked_until:
        remaining_seconds = int(
            (blocked_until - now).total_seconds()
        )

        return False, max(remaining_seconds, 1)

    # Lockout has expired.
    record.attempts = 0
    record.blocked_until = None
    record.window_started_at = now

    db.commit()

    return True, 0


def record_failed_attempt(
    db: Session,
    action: str,
    identifier: str,
) -> bool:
    hashed_identifier = hash_identifier(identifier)
    now = get_utc_now()

    record = (
        db.query(AuthAttempt)
        .filter(
            AuthAttempt.action == action,
            AuthAttempt.identifier == hashed_identifier,
        )
        .with_for_update()
        .first()
    )

    if record is None:
        record = AuthAttempt(
            action=action,
            identifier=hashed_identifier,
            attempts=1,
            window_started_at=now,
        )

        db.add(record)
        db.commit()

        return False

    # Do not continue counting during an active lockout.
    if record.blocked_until is not None:
        blocked_until = normalize_datetime(
            record.blocked_until
        )

        if now < blocked_until:
            return True

        # Lockout expired. Start a new attempt cycle.
        record.attempts = 0
        record.blocked_until = None
        record.window_started_at = now

    record.attempts += 1

    if record.attempts >= MAX_ATTEMPTS:
        record.blocked_until = now + timedelta(
            hours=LOCKOUT_HOURS
        )

        db.commit()
        return True

    db.commit()
    return False


def reset_attempts(
    db: Session,
    action: str,
    identifier: str,
) -> None:
    record = get_attempt_record(
        db,
        action,
        identifier,
    )

    if record is not None:
        db.delete(record)
        db.commit()
