from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw
from app import state as app_state


def _rounded_mask(size, radius: int):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
    return mask


def update_thumbnail(is_test: bool = False) -> Tuple[Optional[int], Optional[Path]]:
    """
    Progressively adds PFPs to a thumbnail (iterating through hard-coded cursor positions):
    1. Reads a hardcoded pfp `app/assets/mock_pfp.jpeg`
    2. Resizes to 214x214 (ignoring aspect ratio) and adds a 50px border radius
    3. Pastes it onto `app/assets/mock_thumbnail.jpeg`

    Returns (index, working_path)
    """
    repo_root = Path(__file__).resolve().parents[2]
    assets_dir = repo_root / "app" / "assets"
    pfp_path = assets_dir / "mock_pfp.jpeg"
    thumb_path = assets_dir / "mock_thumbnail.jpeg"

    # load and prepare images
    try:
        pfp = Image.open(pfp_path).convert("RGBA")
    except Exception:
        return None, None

    # choose resampling
    resample = (
        Image.Resampling.LANCZOS
        if hasattr(Image, "Resampling")
        else getattr(Image, "LANCZOS", 3)
    )
    pfp_resized = pfp.resize((214, 214), resample)

    try:
        base = Image.open(thumb_path).convert("RGBA")
    except Exception:
        return None, None

    mask = _rounded_mask((214, 214), radius=50)

    # top-level generated folder (sibling to `app`)
    gen_root = repo_root / "generated_thumbnail"
    gen_root.mkdir(parents=True, exist_ok=True)

    working_name = (
        "mock_thumbnail_working_test.jpg"
        if is_test
        else "mock_thumbnail_working_official.jpg"
    )
    working_path = gen_root / working_name

    # claim an index via state
    idx = app_state.fetch_and_increment_next_pfp_position(is_test=is_test)
    if idx is None:
        return None, working_path

    # paste avatars from 0..idx inclusive
    composed = base.copy()
    for i in range(0, idx + 1):
        pos = app_state.POSITIONS[i]
        composed.paste(pfp_resized, pos, mask)

    # overwrite the working image
    composed.convert("RGB").save(working_path, format="JPEG", quality=90)

    return idx, working_path
