from googleapiclient.discovery import build
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from app.routes import (
    farm_engagement,
    ping,
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
    # Expose the YouTube API client as a singleton to avoid recreating
    if not (api_key := os.getenv("YOUTUBE_API_KEY")):
        raise HTTPException(status_code=500, detail="Missing YOUTUBE_API_KEY")

    app.state.youtube = build("youtube", "v3", developerKey=api_key)

    try:
        yield
    finally:
        # No close function to call, but remove the ref for GC to collect
        app.state.youtube = None


app = FastAPI(lifespan=lifespan)

app.include_router(ping.router)
app.include_router(farm_engagement.router)
app.include_router(test_fetch_comments.router)
app.include_router(test_create_thumbnail.router)
app.include_router(test_upload_thumbnail.router)
