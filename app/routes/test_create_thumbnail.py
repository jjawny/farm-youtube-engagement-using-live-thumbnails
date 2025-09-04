from app.services.image_service import generate_thumbnail, ImageServiceError
from app.constants import MOCK_PFP_PATH, OUTPUT_TEST_THUMBNAIL
from fastapi.responses import JSONResponse
from app.config import get_http_client
from fastapi import APIRouter, Depends
from typing import Union, List
from pathlib import Path

router = APIRouter()


@router.get("/test-create-thumbnail")
async def test_create_thumbnail(repeat: int = 1, http_session=Depends(get_http_client)):
    repeat = max(1, int(repeat))
    pfp_sources: List[Union[str, Path]] = [Path(MOCK_PFP_PATH) for _ in range(repeat)]

    try:
        out_path = generate_thumbnail(OUTPUT_TEST_THUMBNAIL, pfp_sources, http_session)
    except ImageServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception:
        return JSONResponse(status_code=500, content={"error": "internal error"})

    out_path_clean = out_path.resolve(strict=True) if out_path else None

    return JSONResponse(status_code=201, content={"output": str(out_path_clean)})
