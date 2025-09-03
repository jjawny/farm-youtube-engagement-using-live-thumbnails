from google.auth.transport.requests import Request as AuthRequest
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from fastapi import Request
from typing import Tuple
import os


def _build_credentials() -> Credentials:
    client_id = os.getenv("OAUTH_CLIENT_ID")
    client_secret = os.getenv("OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("OAUTH_REFRESH_TOKEN")
    token_uri = "https://oauth2.googleapis.com/token"
    scopes = [s.strip() for s in os.getenv("OAUTH_SCOPES", "").split(",") if s.strip()]

    if not (client_id and client_secret and refresh_token and scopes):
        raise RuntimeError("Missing OAuth client credentials or refresh token")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )

    return creds


def build_youtube() -> Tuple[Credentials, Resource]:
    """
    Returns a new YouTube client and credentials object.
    """
    creds = _build_credentials()
    creds.refresh(AuthRequest())
    youtube = build("youtube", "v3", credentials=creds)
    return creds, youtube


def get_youtube(request: Request) -> Resource:
    """
    Return the existing YouTube client singleton and credentials from app.state.

    Refresh credentials if expired.
    """
    youtube = getattr(request.app.state, "youtube", None)
    creds = getattr(request.app.state, "youtube_creds", None)

    # Happy path: client exists and creds still usable
    if youtube and creds:
        try:
            if getattr(creds, "valid", False):
                return youtube
            # If expired, refresh and rebuild
            if getattr(creds, "expired", False) or not getattr(creds, "valid", False):
                creds.refresh(AuthRequest())
                client = build("youtube", "v3", credentials=creds)
                request.app.state.youtube = client
                return client
        except Exception:
            # Fall through to rebuild
            # TODO: Add logging
            pass

    # Rebuild
    creds, client = build_youtube()
    request.app.state.youtube = client
    request.app.state.youtube_creds = creds
    return client
