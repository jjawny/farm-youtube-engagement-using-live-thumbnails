from contextlib import asynccontextmanager
from app.config import build_youtube
from dotenv import load_dotenv
from fastapi import FastAPI
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
    # Expose the YouTube client as a singleton
    creds, client = build_youtube()
    app.state.youtube = client
    app.state.youtube_creds = creds

    try:
        yield
    finally:
        # Signal GC to come collect
        app.state.youtube = None


app = FastAPI(lifespan=lifespan)

app.include_router(ping.router)
app.include_router(farm_engagement.router)
app.include_router(test_fetch_comments.router)
app.include_router(test_create_thumbnail.router)
app.include_router(test_upload_thumbnail.router)
