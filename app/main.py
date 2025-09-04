from contextlib import asynccontextmanager
from requests.adapters import HTTPAdapter
from app.config import build_youtube
from dotenv import load_dotenv
from fastapi import FastAPI
import requests
from app.routes import (
    ping,
    debug_youtube_access,
    farm_engagement,
    test_fetch_comments,
    test_create_thumbnail,
    test_upload_thumbnail,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Exposes shared resources for the lifespan of the web API; like a lightweight DI container.
    """
    # Expose the YouTube client as a singleton
    creds, client = build_youtube()
    app.state.youtube = client
    app.state.youtube_creds = creds

    # Expose a shared HTTP session for connection pooling (mostly for the frequent PFP downloads)
    adapter = HTTPAdapter(pool_connections=2, pool_maxsize=20)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    app.state.http_session = session

    try:
        yield
    finally:
        # Clean-up shared HTTP session
        try:
            app.state.http_session.close()
            app.state.http_session = None
        except Exception:
            pass
        # Clean-up YouTube client; no close function to call, signal GC to come collect
        try:
            app.state.youtube = None
            app.state.youtube_creds = None
        except Exception:
            pass


app = FastAPI(lifespan=lifespan)

app.include_router(ping.router)
app.include_router(debug_youtube_access.router)
app.include_router(farm_engagement.router)
app.include_router(test_fetch_comments.router)
app.include_router(test_create_thumbnail.router)
app.include_router(test_upload_thumbnail.router)
