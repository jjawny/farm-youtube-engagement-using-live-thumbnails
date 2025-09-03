from app.services.youtube_service import fetch_comments_async
from fastapi import APIRouter, Depends
from app.config import get_youtube

router = APIRouter()


@router.get("/test-fetch-comments")
async def test_fetch_comments(
    video_id: str, limit: int = 100, youtube=Depends(get_youtube)
):
    result = await fetch_comments_async(youtube, video_id, limit)
    return result
