from datetime import datetime

from pydantic import BaseModel

from app.health.engine import health_engine
from app.history.telemetry_history import telemetry_history_store
from app.models.prediction_service import PredictionService
from app.repositories.mock_asset_repository import mock_asset_repository


class TrendPoint(BaseModel):
    timestamp: str
    value: float


class FleetAnalytics(BaseModel):
    failureTrends: list[TrendPoint]
    fleetHealthTrends: list[TrendPoint]
    predictedFailures: int
    downtimeAvoided: float
    assetsWithHighestRisk: list[str]
    averagePredictionConfidence: float


class AnalyticsService:
    def __init__(self, ml_prediction_service: PredictionService | None = None) -> None:
        self._ml_prediction_service = ml_prediction_service or PredictionService()

    def get_fleet_analytics(self) -> FleetAnalytics:
        assets = mock_asset_repository.list_assets()
        ml_predictions = self._ml_prediction_service.predict_assets(assets)

        failure_trends = self._failure_trends(ml_predictions)
        health_trends = self._health_trends()

        predicted_failures = len([prediction for prediction in ml_predictions if prediction.probability >= 0.7])
        average_confidence = (
            round(sum(prediction.confidence for prediction in ml_predictions) / len(ml_predictions), 2)
            if ml_predictions
            else 0.0
        )
        top_risk_assets = [prediction.assetId for prediction in sorted(ml_predictions, key=lambda item: item.probability, reverse=True)[:3]]

        return FleetAnalytics(
            failureTrends=failure_trends,
            fleetHealthTrends=health_trends,
            predictedFailures=predicted_failures,
            downtimeAvoided=round(predicted_failures * 2.1, 2),
            assetsWithHighestRisk=top_risk_assets,
            averagePredictionConfidence=average_confidence,
        )

    def _failure_trends(self, ml_predictions) -> list[TrendPoint]:
        now = datetime.utcnow()
        trend_points: list[TrendPoint] = []

        for offset in range(6):
            timestamp = now.replace(hour=max(0, now.hour - (5 - offset))).isoformat() + "Z"
            value = len([prediction for prediction in ml_predictions if prediction.probability >= (0.55 + (offset * 0.04))])
            trend_points.append(TrendPoint(timestamp=timestamp, value=float(value)))

        return trend_points

    def _health_trends(self) -> list[TrendPoint]:
        history = telemetry_history_store.list_all_history()
        assets_by_id = {asset.asset.id: asset for asset in mock_asset_repository.list_assets()}

        trend_points: list[TrendPoint] = []
        for index in range(0, 36, 6):
            scores: list[int] = []
            timestamp = None
            for asset_id, samples in history.items():
                if index >= len(samples):
                    continue
                telemetry = samples[index]
                timestamp = timestamp or telemetry.recordedAt
                asset_overview = assets_by_id.get(asset_id)
                if asset_overview is None:
                    continue

                historical_overview = asset_overview.model_copy(update={"telemetry": telemetry})
                historical_health = health_engine.evaluate_asset(historical_overview)
                scores.append(historical_health.healthScore)

            trend_points.append(
                TrendPoint(
                    timestamp=timestamp or datetime.utcnow().isoformat() + "Z",
                    value=round(sum(scores) / len(scores), 2) if scores else 0.0,
                )
            )

        return trend_points


analytics_service = AnalyticsService()
