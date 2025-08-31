from typing import NotRequired, TypedDict


class HealthCheckResponse(TypedDict):
    is_healthy: bool
    error: NotRequired[str]
