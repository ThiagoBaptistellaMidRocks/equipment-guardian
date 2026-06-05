from fastapi import APIRouter, HTTPException

from app.domain.assets import AssetOverview
from app.repositories.mock_asset_repository import mock_asset_repository

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetOverview])
def list_assets() -> list[AssetOverview]:
    return mock_asset_repository.list_assets()


@router.get("/{asset_id}", response_model=AssetOverview)
def get_asset(asset_id: str) -> AssetOverview:
    asset = mock_asset_repository.get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset
