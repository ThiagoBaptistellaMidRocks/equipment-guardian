import re

from app.domain.assets import AssetOverview
from app.storage.repositories.mock_asset_repository import mock_asset_repository


class AssetTool:
    def list_assets(self) -> list[AssetOverview]:
        return mock_asset_repository.list_assets()

    def get_asset(self, asset_id: str) -> AssetOverview | None:
        return mock_asset_repository.get_asset(asset_id)

    def extract_asset_ids(self, message: str) -> list[str]:
        matches = re.findall(r"\b[A-Z]{2}-\d{2}\b", message.upper())
        available_ids = {asset.asset.id for asset in self.list_assets()}
        return [asset_id for asset_id in matches if asset_id in available_ids]
