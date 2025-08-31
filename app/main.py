from googleapiclient.discovery import build
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.routes import engagement, ping
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Exposes shared resources for the lifespan of the web API; like a lightweight DI container.
    """
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
app.include_router(engagement.router)
