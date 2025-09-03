from app.services.youtube_service import upload_thumbnail_async
from fastapi import APIRouter, Depends, HTTPException
from app.config import get_youtube
from pathlib import Path
from app.constants import (
    OUTPUT_TEST_THUMBNAIL,
    OUTPUT_THUMBNAIL_PATH,
)

router = APIRouter()


@router.get("/test-upload-thumbnail")
async def test_upload_thumbnail(
    video_id: str,
    youtube=Depends(get_youtube),
):
    test_thumbnail_path: Path = Path(OUTPUT_THUMBNAIL_PATH) / OUTPUT_TEST_THUMBNAIL

    if not test_thumbnail_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"test thumbnail not found, please test step 2",
        )

    res = await upload_thumbnail_async(youtube, video_id, test_thumbnail_path)

    return {"api_response": res}
