from app.domain.assets import AssetOverview
from app.health.engine import health_engine
from app.health.models import AssetAlert


def list_active_alerts(asset_overviews: list[AssetOverview]) -> list[AssetAlert]:
    return health_engine.list_alerts(asset_overviews)
