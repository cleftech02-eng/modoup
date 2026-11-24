from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from model import User, Activity, EmailVerification
from auth.password import hash_password
from schemes.user import UserCreate
from services.email_service import (
    generate_verification_token,
    hash_verification_token,
    get_verification_expiry,
    create_verification_link,
    build_verification_email,
    send_verification_email,
)
from services.google_auth import verify_google_token
from auth.jwt import create_access_token

logger = logging.getLogger(__name__)


def register_user(db: Session, user_data: UserCreate) -> User:

    # 1. Normalize the email
    email = str(user_data.email).strip().lower()

    # 2. Check whether the email already exists
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise ValueError("Email already registered")

    # 3. Hash the password
    hashed_password = hash_password(user_data.password)

    # 4. Create the user
    new_user = User(
        full_name=user_data.full_name,
        email=email,
        password_hash=hashed_password,
        is_verified=False,
        auth_provider="local",
        hp=100,
        level=1
    )

    # 5. Generate verification token
    raw_token = generate_verification_token()
    token_hash = hash_verification_token(raw_token)

    try:
        # 6. Add the user to the database
        db.add(new_user)

        # Generate the user's database ID
        db.flush()

        # 7. Create verification record
        verification = EmailVerification(
            user_id=new_user.id,
            token_hash=token_hash,
            expires_at=get_verification_expiry(),
            resend_count=0
        )

        db.add(verification)

        # 8. Record signup activity
        activity = Activity(
            user_id=new_user.id,
            type="signup",
            message=f"{new_user.full_name} joined Modo Up!"
        )

        db.add(activity)

        # 9. Commit all database records together
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise ValueError("Email already registered")

    # 10. Create the verification email
    verification_link = create_verification_link(raw_token)

    email_message = build_verification_email(
        email=email,
        verification_link=verification_link
    )

    # 11. Attempt to send the verification email
    try:
        send_verification_email(email_message)

    except Exception:
        logger.exception(
            "Verification email could not be sent to %s",
            email
        )

    return new_user


def authenticate_google_user(db: Session, google_token: str):

    # 1. Verify the Google ID token
    google_user = verify_google_token(google_token)

    if google_user is None:
        raise ValueError("Invalid Google authentication token")

    google_id = google_user["google_id"]
    email = google_user["email"]
    full_name = google_user["full_name"]

    # 2. Check whether this Google account already exists
    user = db.query(User).filter(
        User.google_id == google_id
    ).first()

    if user:
        return user, create_access_token(user.id)

    # 3. Check whether this email belongs to an existing account
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise ValueError(
            "An account with this email already exists. "
            "Please log in using your original method."
        )

    # 4. Create a new Google user
    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=None,
        google_id=google_id,
        auth_provider="google",
        is_verified=True,
        hp=100,
        level=1
    )

    try:
        db.add(new_user)
        db.flush()

        # 5. Record signup activity
        activity = Activity(
            user_id=new_user.id,
            type="signup",
            message=f"{new_user.full_name} joined Modo Up!"
        )

        db.add(activity)

        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise ValueError("Could not create Google account. Please try again.")

    # 6. Generate MODO UP JWT
    access_token = create_access_token(new_user.id)

    return new_user, access_token
