from threading import Lock
from typing import Optional, Tuple, List

# Coordinates (top-left) to paste images on the thumbnail
POSITIONS: List[Tuple[int, int]] = [
    (60, 195),
    (297, 195),
    (534, 195),
    (771, 195),
    (1008, 195),
]

# Two separate counters
_test_lock = Lock()
_test_idx = 0

_official_lock = Lock()
_official_idx = 0


def fetch_and_increment_next_pfp_position(is_test: bool = False) -> Optional[int]:
    """
    NOTE:
    - This is an in-memory DB for demo purposes
    - Recommending swapping this data-access function to read/write to an external DB
    """
    global _test_idx, _official_idx

    limit = len(POSITIONS)

    if is_test:
        with _test_lock:
            if _test_idx >= limit:
                return None
            idx = _test_idx
            _test_idx += 1
            return idx

    with _official_lock:
        if _official_idx >= limit:
            return None
        idx = _official_idx
        _official_idx += 1
        return idx
