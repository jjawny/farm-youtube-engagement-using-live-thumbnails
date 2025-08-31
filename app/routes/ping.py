from app.models.health_check_response import (
    HealthCheckResponse,
)
from fastapi import APIRouter
import httpx
import os

router = APIRouter()


def _check_youtube_api_key() -> HealthCheckResponse:
    # Why not make a call to validate the key? YouTube's daily API quota is limited...
    return HealthCheckResponse(is_healthy=bool(os.getenv("YOUTUBE_API_KEY")))


async def _check_youtube_video() -> HealthCheckResponse:
    yt_video_id = os.getenv("YOUTUBE_VIDEO_ID")

    if not yt_video_id:
        return HealthCheckResponse(is_healthy=False, error="Missing YOUTUBE_VIDEO_ID")

    oembed_url = f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v={yt_video_id}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(oembed_url)
        return HealthCheckResponse(is_healthy=response.status_code == 200)
    except Exception as ex:
        return HealthCheckResponse(is_healthy=False, error=str(ex))


@router.get("/ping")
async def ping():
    return {
        "YOUTUBE_API_KEY": _check_youtube_api_key(),
        "YOUTUBE_VIDEO_ID": await _check_youtube_video(),
    }
