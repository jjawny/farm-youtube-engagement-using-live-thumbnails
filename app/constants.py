from typing import List, Tuple
from pathlib import Path

# Coordinates (top-left) for each image on the thumbnail
POSITIONS: List[Tuple[int, int]] = [
    (60, 195),
    (297, 195),
    (534, 195),
    (771, 195),
    (1008, 195),
]

# Base path for services to read/write from
BASE_PATH: Path = Path(__file__).resolve().parent  # ./app

# Relative path from the base path
MOCK_PFP_PATH = BASE_PATH / "assets/mock_pfp.jpeg"
BASE_THUMBNAIL_PATH = BASE_PATH / "assets/base_thumbnail.jpeg"
OUTPUT_THUMBNAIL_PATH = (
    BASE_PATH / "../generated_thumbnail"
)  # the file_name is a parameter

# Pixel sizes
PFP_SIZE = (214, 214)
PFP_BORDER_RADIUS = 50
