from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pathlib import Path
from PIL import Image, ImageDraw
import threading

router = APIRouter()


# Predefined top-left coordinates (x, y)
POSITIONS = [(60, 195), (297, 195), (534, 195), (771, 195), (1008, 195)]
# Module-level index stored in memory; resets when the webapi restarts
_current_index = 0
_index_lock = threading.Lock()


def _rounded_mask(size, radius: int):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    # rounded rectangle
    draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
    return mask


@router.get("/test-create-thumbnail")
async def test_create_thumbnail():
    """
    Tests progressively adding PFPs to a thumbnail (iterating through hard-coded cursor positions):
    1. Reads a hardcoded pfp `app/assets/mock_pfp.jpeg`
    2. Resizes to 214x214 (ignoring aspect ratio) and adds a 50px border radius
    3. Pastes it onto `app/assets/mock_thumbnail.jpeg`
    4. Outputs to `app/../generated_thumbail/mock_thumbnail_working.jepg`
    """
    global _current_index

    repo_root = Path(__file__).resolve().parents[2]
    assets_dir = repo_root / "app" / "assets"
    pfp_path = assets_dir / "mock_pfp.jpeg"
    thumb_path = assets_dir / "mock_thumbnail.jpeg"

    # load images
    pfp = Image.open(pfp_path).convert("RGBA")
    # ignore aspect ratio as requested
    pfp_resized = pfp.resize(
        (214, 214),
        (
            Image.Resampling.LANCZOS
            if hasattr(Image, "Resampling")
            else getattr(Image, "LANCZOS", 3)
        ),
    )

    base = Image.open(thumb_path).convert("RGBA")

    # build rounded mask for the pasted avatar
    mask = _rounded_mask((214, 214), radius=50)

    out_dir = repo_root / "generated_thumbnail"
    out_dir.mkdir(parents=True, exist_ok=True)

    working_name = "mock_thumbnail_working.jpeg"
    working_path = out_dir / working_name

    # If already full, return early
    with _index_lock:
        if _current_index >= len(POSITIONS):
            # return path if exists, otherwise indicate full but no image
            return JSONResponse(
                status_code=409,
                content={
                    "status": "image full",
                    "generated_image": (
                        str(working_path.relative_to(Path.cwd()))
                        if working_path.exists()
                        else None
                    ),
                },
            )

        # index to paint up to (inclusive)
        idx = _current_index
        # advance index for next request
        _current_index = _current_index + 1

    # rebuild working image from the original mock thumbnail, then paste PFPs up to idx
    composed = base.copy()
    for i in range(0, idx + 1):
        pos = POSITIONS[i]
        composed.paste(pfp_resized, pos, mask)

    # overwrite the working image
    composed.convert("RGB").save(working_path, format="JPEG", quality=90)

    status_code = 201 if idx == 0 else 200

    return JSONResponse(
        status_code=status_code,
        content={
            "output": str(working_path.relative_to(Path.cwd())),
            "index": idx,
        },
    )
