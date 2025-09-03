from typing import Optional, Union, Sequence
from PIL import Image, ImageDraw
from pathlib import Path
from io import BytesIO
import requests
from app.constants import (
    OUTPUT_THUMBNAIL_PATH,
    BASE_THUMBNAIL_PATH,
    PFP_BORDER_RADIUS,
    POSITIONS,
    BASE_PATH,
    PFP_SIZE,
)


class ImageServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _rounded_mask(size, border_radius: int):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    draw.rounded_rectangle([(0, 0), (w, h)], radius=border_radius, fill=255)
    return mask


def _load_image(src: Union[str, Path]) -> Optional[Image.Image]:
    # If a URL
    if isinstance(src, str) and (
        src.startswith("http://") or src.startswith("https://")
    ):
        try:
            resp = requests.get(src, timeout=6)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content)).convert("RGBA")
        except Exception:
            return None

    # If a local path of Path type
    if isinstance(src, Path):
        try:
            return Image.open(src).convert("RGBA")
        except Exception:
            return None

    # If a local path of string type
    p = Path(src)
    local_path = p if p.is_absolute() else BASE_PATH / src

    try:
        return Image.open(local_path).convert("RGBA")
    except Exception:
        return None


def generate_thumbnail(
    output_name: str, pfp_sources: Sequence[Union[str, Path]]
) -> Optional[Path]:
    """
    Pastes the first n position PFPs onto the base thumbnail.
    """
    try:
        base = Image.open(Path(BASE_THUMBNAIL_PATH)).convert("RGBA")
    except Exception:
        raise ImageServiceError("base thumbnail not found or not loadable", 500)

    # prepare the mask for rounded corners
    mask = _rounded_mask(PFP_SIZE, border_radius=PFP_BORDER_RADIUS)

    # prepare the output path
    gen_root = Path(OUTPUT_THUMBNAIL_PATH)
    gen_root.mkdir(parents=True, exist_ok=True)
    out_path = gen_root / output_name

    composed = base.copy()

    # iterate pfps up to positions length
    has_processed_at_least_one_pfp = False

    for idx, src in enumerate(pfp_sources[: len(POSITIONS)]):
        if not (img := _load_image(src)):
            continue

        # resize ignoring aspect ratio
        resample = (
            Image.Resampling.LANCZOS
            if hasattr(Image, "Resampling")
            else getattr(Image, "LANCZOS", 3)
        )
        pfp_resized = img.resize(PFP_SIZE, resample)
        pos = POSITIONS[idx]
        composed.paste(pfp_resized, pos, mask)
        has_processed_at_least_one_pfp = True

    if not has_processed_at_least_one_pfp:
        raise ImageServiceError("no valid source images provided", 400)

    composed.convert("RGB").save(out_path, format="JPEG", quality=90)
    return out_path
