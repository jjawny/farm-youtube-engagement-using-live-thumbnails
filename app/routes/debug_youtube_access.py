from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.config import get_youtube
from app.services.youtube_service import (
    list_my_channels_and_videos,
    YouTubeServiceError,
)

router = APIRouter()


@router.get("/debug-youtube-access")
async def debug_youtube_access(youtube=Depends(get_youtube)):
    try:
        return list_my_channels_and_videos(youtube)
    except YouTubeServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"failed to list your channel and videos, reason: {ex}",
        )
