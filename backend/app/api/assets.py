from fastapi import APIRouter, HTTPException

from app.domain.assets import AssetOverview
from app.storage.timeline_service import AssetHistoryResponse, AssetTimelineResponse, timeline_service
from app.storage.repositories.mock_asset_repository import mock_asset_repository

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


@router.get("/{asset_id}/history", response_model=AssetHistoryResponse)
def get_asset_history(asset_id: str) -> AssetHistoryResponse:
    history = timeline_service.get_asset_history(asset_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return history


@router.get("/{asset_id}/timeline", response_model=AssetTimelineResponse)
def get_asset_timeline(asset_id: str) -> AssetTimelineResponse:
    timeline = timeline_service.get_asset_timeline(asset_id)
    if timeline is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return timeline
