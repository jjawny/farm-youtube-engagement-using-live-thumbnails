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

# Base path
BASE_PATH: Path = Path(__file__).resolve().parent  # ./app

# Input paths
MOCK_PFP_PATH = BASE_PATH / "assets/mock_pfp.jpeg"
BASE_THUMBNAIL_PATH = BASE_PATH / "assets/base_thumbnail.jpeg"

# Output paths
OUTPUT_THUMBNAIL_PATH = BASE_PATH / "../generated_thumbnail"
OUTPUT_OFFICIAL_THUMBNAIL = "thumbnail.jpeg"
OUTPUT_TEST_THUMBNAIL = "test_thumbnail.jpeg"

# Pixel sizes
PFP_SIZE = (214, 214)
PFP_BORDER_RADIUS = 50
