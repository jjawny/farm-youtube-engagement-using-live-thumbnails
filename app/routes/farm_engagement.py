from app.services.image_service import generate_thumbnail, ImageServiceError
from app.constants import OUTPUT_OFFICIAL_THUMBNAIL, POSITIONS
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from app.config import get_youtube
from typing import List
from app.services.youtube_service import (
    fetch_comments_async,
    upload_thumbnail_async,
    YouTubeServiceError,
)

router = APIRouter()


@router.get("/farm-engagement")
async def farm_engagement(
    video_id: str, limit: int = 100, youtube=Depends(get_youtube)
):
    # 1. Fetch comments
    try:
        fetch_comments_response = await fetch_comments_async(youtube, video_id, limit)
    except YouTubeServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception as ex:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"failed to fetch comments for video '{video_id}', reason: {ex}"
            },
        )

    # 2. De-dupe PFP urls and keep the highest like count seen for each unique PFP
    pfp_max_likes = {}
    for comment in fetch_comments_response.get("comments", []):
        if not (pfp := comment.get("pfp")):
            continue
        like_count = int(comment.get("like_count") or 0)
        existing = pfp_max_likes.get(pfp)
        if existing is None or like_count > existing:
            pfp_max_likes[pfp] = like_count

    # 3. Order unique PFPs by like count desc
    ordered_pfps: List[str] = [
        pfp
        for pfp, _ in sorted(pfp_max_likes.items(), key=lambda kv: kv[1], reverse=True)
    ]

    # 4. Limit to available positions to avoid unnecessary downloads
    ordered_pfps = ordered_pfps[: len(POSITIONS)]

    # 5. Generate thumbnail
    try:
        out_path = generate_thumbnail(OUTPUT_OFFICIAL_THUMBNAIL, ordered_pfps)
    except ImageServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception as ex:
        return JSONResponse(
            status_code=500, content={"error": f"thumbnail generation failed: {ex}"}
        )

    # 6. Upload to YouTube
    try:
        youtube_response = await upload_thumbnail_async(youtube, video_id, out_path)
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
