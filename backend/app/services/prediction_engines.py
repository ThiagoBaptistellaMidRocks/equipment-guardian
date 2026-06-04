from typing import Protocol

from app.domain.assets import AssetType


class PredictionEngine(Protocol):
    supported_asset_type: AssetType

    def engine_name(self) -> str:
        """Return the prediction engine identifier."""
