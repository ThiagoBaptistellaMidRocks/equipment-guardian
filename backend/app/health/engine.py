from app.domain.assets import Asset, AssetHealth, AssetOverview, AssetTelemetry
from app.health.calculator import HealthCalculator
from app.health.models import AssetAlert


class HealthEngine:
    def __init__(self, calculator: HealthCalculator | None = None) -> None:
        self._calculator = calculator or HealthCalculator()

    def evaluate(self, asset: Asset, telemetry: AssetTelemetry) -> AssetHealth:
        return self._calculator.calculate(asset, telemetry)

    def evaluate_asset(self, asset_overview: AssetOverview) -> AssetHealth:
        return self.evaluate(asset_overview.asset, asset_overview.telemetry)

    def evaluate_assets(self, asset_overviews: list[AssetOverview]) -> list[AssetHealth]:
        return [self.evaluate_asset(asset_overview) for asset_overview in asset_overviews]

    def list_alerts(self, asset_overviews: list[AssetOverview]) -> list[AssetAlert]:
        alerts: list[AssetAlert] = []

        for asset_overview in asset_overviews:
            health = self.evaluate_asset(asset_overview)
            for alert in health.activeAlerts:
                alerts.append(
                    AssetAlert(
                        assetId=asset_overview.asset.id,
                        assetName=asset_overview.asset.name,
                        assetType=asset_overview.asset.assetType,
                        riskLevel=health.riskLevel,
                        code=alert.code,
                        message=alert.message,
                        severity=alert.severity,
                        metric=alert.metric,
                        value=alert.value,
                        threshold=alert.threshold,
                    )
                )

        return alerts


health_engine = HealthEngine()
