from collections.abc import Callable
from typing import Literal

from fastapi import HTTPException, status

from src.config import settings

FeatureName = Literal["test_drives", "service_appointments", "custom_orders", "reviews", "favorites"]


def require_feature(feature: FeatureName) -> Callable[[], None]:
    """Dependency that hides endpoints of a feature switched off in the brand config."""

    def check() -> None:
        if not getattr(settings.brand_settings.features, feature):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature is disabled")

    return check
