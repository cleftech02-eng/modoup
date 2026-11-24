import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from model import User, PasswordReset
from auth.password import hash_password
from services.email_service import (
    generate_password_reset_token,
    hash_password_reset_token,
    get_password_reset_expiry,
    create_password_reset_link,
    build_password_reset_email,
    send_password_reset_email,
)

logger = logging.getLogger(__name__)


def request_password_reset(db: Session, email: str) -> None:
    normalized_email = email.strip().lower()

    user = db.query(User).filter(
        User.email == normalized_email
    ).first()

    # Return silently if the account does not exist.
    # The API will show the same message either way.
    if user is None:
        return

    raw_token = generate_password_reset_token()
    token_hash = hash_password_reset_token(raw_token)

    reset_record = db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id
    ).first()

    if reset_record:
        reset_record.token_hash = token_hash
        reset_record.expires_at = get_password_reset_expiry()
        reset_record.used_at = None
        reset_record.created_at = datetime.now(timezone.utc)
    else:
        reset_record = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=get_password_reset_expiry(),
            used_at=None
        )
        db.add(reset_record)

    db.commit()

    reset_link = create_password_reset_link(raw_token)

    email_message = build_password_reset_email(
        email=user.email,
        reset_link=reset_link
    )

    try:
        send_password_reset_email(email_message)
    except Exception:
        logger.exception(
            "Password reset email failed for user ID %s",
            user.id
        )


def reset_user_password(
    db: Session,
    token: str,
    new_password: str
) -> bool:

    token_hash = hash_password_reset_token(token)

    reset_record = db.query(PasswordReset).filter(
        PasswordReset.token_hash == token_hash
    ).first()

    if reset_record is None:
        return False

    now = datetime.now(timezone.utc)

    expires_at = reset_record.expires_at

    # PostgreSQL may return a naive datetime depending on configuration.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if reset_record.used_at is not None:
        return False

    if now > expires_at:
        return False

    user = db.query(User).filter(
        User.id == reset_record.user_id
    ).first()

    if user is None:
        return False

    user.password_hash = hash_password(new_password)
    reset_record.used_at = now

    db.commit()

    return True
