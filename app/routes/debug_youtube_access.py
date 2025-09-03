from app.services.youtube_service import list_my_channels_and_videos
from fastapi import APIRouter, Depends
from app.config import get_youtube

router = APIRouter()


@router.get("/debug-youtube-access")
async def debug_youtube_access(youtube=Depends(get_youtube)):
    return list_my_channels_and_videos(youtube)
