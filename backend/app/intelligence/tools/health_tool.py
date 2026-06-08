from app.health.engine import health_engine
from app.storage.repositories.mock_asset_repository import mock_asset_repository


class HealthTool:
    def get_asset_health(self, asset_id: str) -> dict | None:
        asset = mock_asset_repository.get_asset(asset_id)
        if asset is None:
            return None

        return asset.health.model_dump()

    def list_health(self) -> list[dict]:
        assets = mock_asset_repository.list_assets()
        return [health.model_dump() for health in health_engine.evaluate_assets(assets)]
