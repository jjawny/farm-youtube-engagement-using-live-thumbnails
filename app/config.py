from google.auth.transport.requests import Request as AuthRequest
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from requests import Session
from fastapi import Request
from threading import Lock
from typing import Tuple
import requests
import os

_CREATE_NEW_HTTP_SESSION_LOCK = Lock()


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
    youtube = build("youtube", "v3", credentials=creds)
    return creds, youtube


def get_youtube(request: Request) -> Resource:
    """
    Return the existing YouTube client singleton and credentials from app.state.

    Refresh credentials if expired.
    """
    youtube = getattr(request.app.state, "youtube", None)
    creds = getattr(request.app.state, "youtube_creds", None)

    if youtube and creds:
        try:
            if (not getattr(creds, "expired", True)) and getattr(creds, "valid", False):
                return youtube

            else:
                try:
                    creds.refresh(AuthRequest())
                    client = build("youtube", "v3", credentials=creds)
                    request.app.state.youtube = client
                    request.app.state.youtube_creds = creds
                    return client
                except Exception:
                    # Continue to rebuild
                    pass
        except Exception:
            # Continue to rebuild
            pass

    # Rebuild
    creds, client = build_youtube()
    try:
        creds.refresh(AuthRequest())
    except Exception:
        # Don't crash, let YouTube API calls fail with clear errors.
        pass

    request.app.state.youtube = client
    request.app.state.youtube_creds = creds
    return client


def get_http_client(request: Request) -> Session:
    existing = getattr(request.app.state, "http_session", None)
    if existing is not None:
        return existing

    # Avoid race-conditions (multiple requests triggering creating a new session)
    with _CREATE_NEW_HTTP_SESSION_LOCK:
        existing = getattr(request.app.state, "http_session", None)
        if existing is not None:
            return existing
        session = requests.Session()
        request.app.state.http_session = session
        return session
