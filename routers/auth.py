from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from model import User, EmailVerification
from auth.password import verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user
from services.email_service import hash_verification_token
from schemes.user import Token, UserCreate, UserOut
from services import auth
from pydantic import BaseModel
from services.auth import authenticate_google_user
import hashlib
from jose import jwt
from auth.dependencies import oauth2_scheme
from model import RevokedToken
from schemes.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from services.password_reset import (
    request_password_reset,
    reset_user_password
)
from config import get_settings
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/")
def root():
    return {
        "message": "Welcome to Modo Up API"
    }
class GoogleAuthRequest(BaseModel):
    token: str

@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth.register_user(db, data)
        return user

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form.username.strip().lower()
    ).first()

    # 1. Check email and password
    if not user or not user.password_hash or not verify_password(
        form.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # 2. Block unverified users
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in."
        )

    # 3. Issue access token
    return Token(
        access_token=create_access_token(user.id)
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Decode the already-validated token to get its expiry
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    expires_at = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc
    )

    # Hash the token before storing it
    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    # Save the revoked token
    revoked_token = RevokedToken(
        token_hash=token_hash,
        expires_at=expires_at
    )

    db.add(revoked_token)
    db.commit()

    return {
        "message": "Successfully logged out."
    }


@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    # 1. Hash the received token
    token_hash = hash_verification_token(token)

    # 2. Find the verification record
    verification = db.query(EmailVerification).filter(
        EmailVerification.token_hash == token_hash
    ).first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification link"
        )

    # 3. Check whether token was already used
    if verification.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link has already been used"
        )

    # 4. Check token expiry
    now = datetime.now(timezone.utc)
    expires_at = verification.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now >= expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired"
        )

    # 5. Find the user
    user = db.query(User).filter(
        User.id == verification.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 6. Verify account and consume token
    user.is_verified = True
    verification.used_at = now

    db.commit()

    return {
        "message": "Email successfully verified. You can now log in."
    }
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    request_password_reset(
        db=db,
        email=str(request.email)
    )

    return {
        "message": "If an account exists with that email, a password reset link will be sent."
    }

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    success = reset_user_password(
        db=db,
        token=request.token,
        new_password=request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset link."
        )

    return {
        "message": "Your password has been reset successfully. You can now log in."
    }

@router.post("/google")
def google_login(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    try:
        user, access_token = authenticate_google_user(
            db=db,
            google_token=request.token
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "is_verified": user.is_verified,
                "hp": user.hp,
                "level": user.level
            }
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )
