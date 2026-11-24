
import hashlib

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from model import User, RevokedToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise error

    # Hash the token before checking the revoked tokens table
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    revoked_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.token_hash == token_hash)
        .first()
    )

    if revoked_token is not None:
        raise error

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise error

    return user
