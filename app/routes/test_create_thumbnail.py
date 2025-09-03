from app.services.image_service import generate_thumbnail, ImageServiceError
from fastapi.responses import JSONResponse
from app.constants import MOCK_PFP_PATH
from fastapi import APIRouter
from pathlib import Path
from typing import Union, List

router = APIRouter()


@router.get("/test-create-thumbnail")
async def test_create_thumbnail(repeat: int = 1):
    repeat = max(1, int(repeat))
    pfp_sources: List[Union[str, Path]] = [Path(MOCK_PFP_PATH) for _ in range(repeat)]

    try:
        out_path = generate_thumbnail("mock_thumbnail_working_test.jpeg", pfp_sources)
    except ImageServiceError as ex:
        return JSONResponse(status_code=ex.status_code, content={"error": ex.message})
    except Exception:
        return JSONResponse(status_code=500, content={"error": "internal error"})

    out_path_clean = out_path.resolve(strict=True) if out_path else None

    return JSONResponse(status_code=201, content={"output": str(out_path_clean)})
