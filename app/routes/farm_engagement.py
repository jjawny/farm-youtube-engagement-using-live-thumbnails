from app.services.youtube_service import get_youtube, fetch_comments_async
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/farm-engagement")
async def farm_engagement(
    video_id: str, limit: int = 100, youtube=Depends(get_youtube)
):
    result = await fetch_comments_async(youtube, video_id, limit)
    return result
