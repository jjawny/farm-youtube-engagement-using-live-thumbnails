from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pathlib import Path
from app.services.image_service import update_thumbnail

router = APIRouter()


@router.get("/test-create-thumbnail")
async def test_create_thumbnail():
    idx, out_path = update_thumbnail(is_test=True)
    if idx is None:
        out_rel = (
            str(out_path.relative_to(Path.cwd()))
            if out_path and out_path.exists()
            else None
        )
        return JSONResponse(
            status_code=409,
            content={"status": "image full", "generated_image": out_rel},
        )

    status_code = 201 if idx == 0 else 200
    out_rel = (
        str(out_path.relative_to(Path.cwd()))
        if out_path and out_path.exists()
        else None
    )
    return JSONResponse(
        status_code=status_code, content={"output": out_rel, "index": idx}
    )
