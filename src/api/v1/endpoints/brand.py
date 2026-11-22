import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Response, status
from fastapi.responses import FileResponse

from src.api.v1.models.brand_models import BrandResponse
from src.brand_config import brand_dir
from src.config import settings

router = APIRouter(prefix="/brand", tags=["Brand"])

# Revalidate on every load (cheap 304 via ETag) so a redeployed brand shows up immediately.
BRAND_CACHE_CONTROL = "no-cache"
ASSET_CACHE_CONTROL = "public, max-age=3600"


def _public_brand() -> tuple[dict[str, Any], str]:
    """Builds the public brand payload and its ETag; reads asset files, so call it off the event loop."""
    data = settings.brand_settings.public_dict()
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return data, f'"{digest[:32]}"'


@router.get(
    "",
    response_model=BrandResponse,
    responses={
        status.HTTP_304_NOT_MODIFIED: {"description": "Brand unchanged since the given ETag"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_brand(
    response: Response,
    if_none_match: str | None = Header(default=None),
) -> BrandResponse | Response:
    """Public white-label configuration of this deployment."""
    data, etag = await asyncio.to_thread(_public_brand)
    headers = {"ETag": etag, "Cache-Control": BRAND_CACHE_CONTROL}
    if if_none_match == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)
    response.headers.update(headers)
    return BrandResponse.model_validate(data)


@router.get(
    "/assets/{file_name}",
    response_class=FileResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Asset not found"}},
)
async def get_brand_asset(file_name: str) -> FileResponse:
    """Serves a file from the mounted brand assets directory."""
    assets_dir = (brand_dir() / "assets").resolve()
    path = (assets_dir / file_name).resolve()
    if not path.is_relative_to(assets_dir) or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return FileResponse(Path(path), headers={"Cache-Control": ASSET_CACHE_CONTROL})
