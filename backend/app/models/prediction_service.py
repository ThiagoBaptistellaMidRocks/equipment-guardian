from collections.abc import Sequence

import xgboost as xgb
from pydantic import BaseModel

from app.domain.assets import AssetOverview, AssetType
from app.ml.feature_builder import FeatureBuilder
from app.models.model_loader import ModelLoader


class MlPrediction(BaseModel):
    assetId: str
    predictedEvent: str
    probability: float
    confidence: int
    modelVersion: str


class PredictionService:
    def __init__(self, model_loader: ModelLoader | None = None, feature_builder: FeatureBuilder | None = None) -> None:
        self._model_loader = model_loader or ModelLoader()
        self._feature_builder = feature_builder or FeatureBuilder()

    def predict_asset(self, asset_overview: AssetOverview) -> MlPrediction | None:
        if asset_overview.asset.assetType != AssetType.HAUL_TRUCK:
            return None

        model = self._model_loader.load_active_model()
        history = self._historical_window(asset_overview)
        features = self._feature_builder.build_features(history)
        probability = self._probability(model, features)

        return MlPrediction(
            assetId=asset_overview.asset.id,
            predictedEvent="TIRE_OVERHEAT",
            probability=probability,
            confidence=round(probability * 100),
            modelVersion=self._model_loader.model_version,
        )

    def predict_assets(self, asset_overviews: Sequence[AssetOverview]) -> list[MlPrediction]:
        predictions: list[MlPrediction] = []
        for asset_overview in asset_overviews:
            prediction = self.predict_asset(asset_overview)
            if prediction is not None:
                predictions.append(prediction)

        return sorted(predictions, key=lambda item: item.probability, reverse=True)

    def _probability(self, model: xgb.Booster, features: dict[str, float]) -> float:
        matrix = xgb.DMatrix([[features[name] for name in self._feature_builder.feature_names]], feature_names=self._feature_builder.feature_names)
        return float(model.predict(matrix)[0])

    def _historical_window(self, asset_overview: AssetOverview) -> list:
        from datetime import datetime, timedelta, timezone
        from app.domain.assets import AssetTelemetry

        current = asset_overview.telemetry
        current_time = datetime.fromisoformat(current.recordedAt.replace("Z", "+00:00"))
        history: list[AssetTelemetry] = []

        for step in range(12):
            offset = 11 - step
            sample_time = current_time - timedelta(minutes=offset * 5)
            sample_measurements = dict(current.measurements)
            growth = 0.92 + (step * 0.012)
            if asset_overview.asset.id in {"HT-07", "HT-11"}:
                growth += 0.05

            for key in ("frontLeftTireC", "frontRightTireC", "rearLeftTireC", "rearRightTireC"):
                if isinstance(sample_measurements.get(key), (int, float)):
                    sample_measurements[key] = round(float(sample_measurements[key]) * growth + 1.5, 2)

            for key in ("frontLeftTirePsi", "frontRightTirePsi", "rearLeftTirePsi", "rearRightTirePsi"):
                if isinstance(sample_measurements.get(key), (int, float)):
                    sample_measurements[key] = round(float(sample_measurements[key]) - (1.2 + step * 0.15), 2)

            if isinstance(sample_measurements.get("speedKph"), (int, float)):
                sample_measurements["speedKph"] = round(float(sample_measurements["speedKph"]) * (0.96 + step * 0.003), 2)

            sample_measurements.setdefault("ambientTemperatureC", 27.0 + (step * 0.2))
            sample_measurements.setdefault("tireAgeHours", 410.0 + (step * 0.75))

            history.append(
                AssetTelemetry(
                    assetId=current.assetId,
                    recordedAt=sample_time.isoformat().replace("+00:00", "Z"),
                    source="synthetic-inference",
                    measurements=sample_measurements,
                )
            )

        return history + [current]
