from googleapiclient.http import MediaFileUpload
from app.constants import BASE_PATH
from typing import Dict, Any, List
from fastapi import HTTPException
from pathlib import Path
import asyncio


def _fetch_comments(youtube, video_id: str, limit: int) -> Dict[str, Any]:
    max_results = max(1, min(int(limit), 100))
    youtube_response = (
        youtube.commentThreads()
        .list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            order="relevance",  # not 1:1 with YouTube's top comments algo, but close enough
        )
        .execute()
    )

    comments: List[Dict[str, Any]] = []
    for item in youtube_response.get("items", []):
        raw_comment = (
            item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
        )
        slim_comment = {
            "like_count": int(raw_comment.get("likeCount") or 0),
            "text": raw_comment.get("textDisplay", ""),
            "pfp": raw_comment.get("authorProfileImageUrl"),
        }
        comments.append(slim_comment)

    comments_ordered_by_likes_desc = sorted(
        comments, key=lambda c: c.get("like_count", 0), reverse=True
    )

    response = {
        "metadata": (youtube_response or {}).get("pageInfo"),
        "comments": comments_ordered_by_likes_desc,
    }
    return response


def _upload_thumbnail(youtube, video_id: str, image_path: Path) -> Dict[str, Any]:
    """Synchronous upload of a video's thumbnail using the provided youtube client.

    Returns the API response dict on success; raises HTTPException on failure.
    """
    try:
        media = MediaFileUpload(str(BASE_PATH / image_path), mimetype="image/jpeg")
        req = youtube.thumbnails().set(videoId=video_id, media_body=media)
        resp = req.execute()
        return resp or {}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"thumbnail upload failed: {ex}")


async def fetch_comments_async(*args, **kwargs) -> Dict[str, Any]:
    """
    Call this async shim to avoid blocking the main thread and other incoming requests (Google's package is synchronous)
    """
    return await asyncio.to_thread(_fetch_comments, *args, **kwargs)


async def upload_thumbnail_async(*args, **kwargs) -> Dict[str, Any]:
    """
    Call this async shim to avoid blocking the main thread and other incoming requests (Google's package is synchronous)
    """
    return await asyncio.to_thread(_upload_thumbnail, *args, **kwargs)
