from app.services.youtube_service import fetch_comments_async, YouTubeServiceError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.config import get_youtube

router = APIRouter()


@router.get("/test-fetch-comments")
async def test_fetch_comments(
    video_id: str, limit: int = 100, youtube=Depends(get_youtube)
):
    try:
        result = await fetch_comments_async(youtube, video_id, limit)
    except YouTubeServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"failed to fetch comments for video '{video_id}', reason: {ex}",
        )

    return result
