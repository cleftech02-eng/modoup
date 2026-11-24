
import secrets
import hashlib

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import smtplib

from config import get_settings

settings = get_settings()


# ==========================================
# EMAIL VERIFICATION
# ==========================================

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_verification_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=5)


def create_verification_link(token: str) -> str:
    return f"http://127.0.0.1:8000/auth/verify-email?token={token}"


def build_verification_email(
    email: str,
    verification_link: str
) -> EmailMessage:

    message = EmailMessage()

    message["Subject"] = "Verify your MODO UP account"
    message["From"] = settings.MAIL_FROM
    message["To"] = email

    message.set_content(
        f"""
Welcome to MODO UP!

You're one step away from starting your learning journey.

Please verify your email by clicking the link below:

{verification_link}

This link expires in 5 hours.

If you did not create a MODO UP account, you can ignore this email.
"""
    )

    return message


def send_verification_email(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD
        )
        server.send_message(message)


# ==========================================
# PASSWORD RESET
# ==========================================

def generate_password_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_password_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_password_reset_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=30)


def create_password_reset_link(token: str) -> str:
    return f"http://127.0.0.1:8000/auth/reset-password?token={token}"


def build_password_reset_email(
    email: str,
    reset_link: str
) -> EmailMessage:

    message = EmailMessage()

    message["Subject"] = "Reset your MODO UP password"
    message["From"] = settings.MAIL_FROM
    message["To"] = email

    message.set_content(
        f"""
Hello,

We received a request to reset your MODO UP password.

Click the link below to choose a new password:

{reset_link}

This link expires in 30 minutes and can only be used once.

If you did not request a password reset, you can ignore this email.

MODO UP Team
"""
    )

    return message


def send_password_reset_email(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD
        )
        server.send_message(message)
