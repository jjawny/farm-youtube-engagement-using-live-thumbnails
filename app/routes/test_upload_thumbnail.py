from fastapi import APIRouter
from pathlib import Path
from PIL import Image, ImageDraw
import threading

router = APIRouter()


@router.get("/test-upload-thumbnail")
async def test_upload_thumbnail():
    return {"status": "TODO"}
