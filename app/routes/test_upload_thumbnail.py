from app.services.youtube_service import upload_thumbnail_async, YouTubeServiceError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
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

    try:
        youtube_response = await upload_thumbnail_async(
            youtube, video_id, test_thumbnail_path
        )
    except YouTubeServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"failed to update thumbnail for video '{video_id}', reason: {ex}"
            },
        )

    return {"youtube_response": youtube_response}
