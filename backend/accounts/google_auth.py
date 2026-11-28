
from google.auth.transport import requests
from google.oauth2 import id_token

from django.conf import settings


def verify_google_token(token):

    try:
        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Ensure the email is verified by Google
        if not id_info.get("email_verified"):
            return None

        return {
            "google_id": id_info.get("sub"),
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
        }

    except ValueError:
        # Invalid, expired or incorrectly issued token
        return None
