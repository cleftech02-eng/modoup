from google.oauth2 import id_token
from google.auth.transport import requests
from config import get_settings
settings = get_settings()
def verify_google_token(token: str):
    """
    Verify a Google ID token and return the user's information.
    """

    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Only accept tokens issued by Google.
        if id_info.get("iss") not in [
            "accounts.google.com",
            "https://accounts.google.com"
        ]:
            return None

        # Require Google to confirm the email address.
        if id_info.get("email_verified") is not True:
            return None

        # Require a Google account ID and email.
        if not id_info.get("sub") or not id_info.get("email"):
            return None

        return {
            "google_id": id_info["sub"],
            "email": id_info["email"].strip().lower(),
            "full_name": id_info.get("name", "MODO UP User"),
            "email_verified": True
        }

    except ValueError:
        return None
