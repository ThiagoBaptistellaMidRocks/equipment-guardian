from fastapi import APIRouter

from app.domain.assets import AssetHealth
from app.health.engine import health_engine
from app.repositories.mock_asset_repository import mock_asset_repository

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=list[AssetHealth])
def list_health() -> list[AssetHealth]:
    assets = mock_asset_repository.list_assets()
    return health_engine.evaluate_assets(assets)
