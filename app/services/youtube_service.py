from fastapi import HTTPException, Request
from typing import Dict, Any, List
import asyncio


def get_youtube(request: Request):
    if not (youtube := getattr(request.app.state, "youtube", None)):
        raise HTTPException(status_code=500, detail="YouTube client not initialized")
    return youtube


def fetch_comments(youtube, video_id: str, limit: int) -> Dict[str, Any]:
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


async def fetch_comments_async(*args, **kwargs) -> Dict[str, Any]:
    """
    Fetching comments using Google's package is synchronous.

    Call this async shim to avoid blocking the main thread and other incoming requests.
    """
    return await asyncio.to_thread(fetch_comments, *args, **kwargs)
