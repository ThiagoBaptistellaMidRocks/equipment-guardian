from fastapi import APIRouter

from app.alerts.service import list_active_alerts
from app.health.models import AssetAlert
from app.storage.repositories.mock_asset_repository import mock_asset_repository

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AssetAlert])
def get_alerts() -> list[AssetAlert]:
    assets = mock_asset_repository.list_assets()
    return list_active_alerts(assets)
