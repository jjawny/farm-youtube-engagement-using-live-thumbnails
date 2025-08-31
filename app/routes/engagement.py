from app.services.youtube import get_youtube, fetch_comments_async
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/farm-comments")
async def farm_comments(video_id: str, limit: int = 100, youtube=Depends(get_youtube)):
    result = await fetch_comments_async(youtube, video_id, limit)
    return result
