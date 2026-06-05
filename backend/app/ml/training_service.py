from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split

from app.domain.assets import AssetTelemetry, AssetType
from app.ml.dataset_builder import DatasetBuilder
from app.ml.evaluation_service import EvaluationService
from app.ml.feature_builder import FeatureBuilder
from app.models.asset_event import AssetEvent, AssetEventSeverity, AssetEventType
from app.models.model_loader import MODEL_PATH, MODEL_VERSION
from app.repositories.mock_asset_repository import mock_asset_repository


class TrainingService:
    def __init__(
        self,
        feature_builder: FeatureBuilder | None = None,
        dataset_builder: DatasetBuilder | None = None,
        evaluation_service: EvaluationService | None = None,
    ) -> None:
        self._feature_builder = feature_builder or FeatureBuilder()
        self._dataset_builder = dataset_builder or DatasetBuilder(self._feature_builder)
        self._evaluation_service = evaluation_service or EvaluationService()

    def train_default_model(self) -> dict[str, float]:
        telemetry_history, asset_events = self._build_default_training_inputs()
        dataset = self._dataset_builder.build_dataset(telemetry_history, asset_events)
        return self.train_from_dataset(dataset)

    def train_from_dataset(self, dataset: pd.DataFrame) -> dict[str, float]:
        if dataset.empty:
            raise ValueError("Training dataset is empty")

        features = self._feature_builder.feature_names
        X = dataset[features]
        y = dataset["event"]

        if y.nunique() < 2:
            raise ValueError("Training dataset must contain both normal and overheat examples")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

        classifier = xgb.XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            n_estimators=120,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )
        classifier.fit(X_train, y_train)

        probabilities = classifier.predict_proba(X_test)[:, 1]
        metrics = self._evaluation_service.evaluate(y_test, probabilities)
        metrics["rows"] = float(len(dataset))

        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        classifier.get_booster().save_model(str(MODEL_PATH))
        self._write_metrics(metrics)
        return metrics

    def ensure_model(self) -> Path:
        if not MODEL_PATH.exists():
            self.train_default_model()
        return MODEL_PATH

    def _write_metrics(self, metrics: dict[str, float]) -> None:
        evaluation_dir = MODEL_PATH.parent.parent / "evaluation"
        evaluation_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = evaluation_dir / f"{MODEL_VERSION}.metrics.json"
        metrics_path.write_text(pd.Series(metrics).to_json(), encoding="utf-8")

    def _build_default_training_inputs(self) -> tuple[list[AssetTelemetry], list[AssetEvent]]:
        telemetry_history: list[AssetTelemetry] = []
        asset_events: list[AssetEvent] = []
        base_time = datetime(2026, 6, 5, 8, 0, tzinfo=timezone.utc)

        for index, asset_overview in enumerate(mock_asset_repository.list_assets()):
            if asset_overview.asset.assetType != AssetType.HAUL_TRUCK:
                continue

            current = asset_overview.telemetry
            current_time = base_time + timedelta(minutes=index * 5)
            current_measurements = dict(current.measurements)
            current_measurements.setdefault("ambientTemperatureC", 28.0 + index)
            current_measurements.setdefault("tireAgeHours", 400.0 + (index * 20))
            current_measurements.setdefault("payloadTonnes", float(current_measurements.get("payloadTonnes", 0) or 0))

            for step in range(12):
                offset = 11 - step
                sample_time = current_time - timedelta(minutes=offset * 5)
                sample_measurements = self._build_sample_measurements(current_measurements, asset_overview.asset.id, step)
                telemetry_history.append(
                    AssetTelemetry(
                        assetId=asset_overview.asset.id,
                        recordedAt=sample_time.isoformat().replace("+00:00", "Z"),
                        source="synthetic-training",
                        measurements=sample_measurements,
                    )
                )

            if asset_overview.health.riskLevel in {"CRITICAL", "HIGH"}:
                asset_events.append(
                    AssetEvent(
                        asset_id=asset_overview.asset.id,
                        event_type=AssetEventType.TIRE_OVERHEAT,
                        event_time=(current_time + timedelta(minutes=25)).isoformat().replace("+00:00", "Z"),
                        severity=AssetEventSeverity.CRITICAL,
                    )
                )
            else:
                asset_events.append(
                    AssetEvent(
                        asset_id=asset_overview.asset.id,
                        event_type=AssetEventType.BRAKE_FAILURE,
                        event_time=(current_time + timedelta(minutes=40)).isoformat().replace("+00:00", "Z"),
                        severity=AssetEventSeverity.LOW,
                    )
                )

        return telemetry_history, asset_events

    def _build_sample_measurements(
        self,
        measurements: dict[str, float | str | bool | None],
        asset_id: str,
        step: int,
    ) -> dict[str, float | str | bool | None]:
        sample = dict(measurements)
        trend_multiplier = 0.88 + (step * 0.01)
        temp_boost = 6.0 if asset_id in {"HT-07", "HT-11"} else 1.5
        pressure_drop = 3.0 if asset_id in {"HT-07", "HT-11"} else 0.5

        for key in ("frontLeftTireC", "frontRightTireC", "rearLeftTireC", "rearRightTireC"):
            if isinstance(sample.get(key), (int, float)):
                sample[key] = round(float(sample[key]) * trend_multiplier + temp_boost, 2)

        for key in ("frontLeftTirePsi", "frontRightTirePsi", "rearLeftTirePsi", "rearRightTirePsi"):
            if isinstance(sample.get(key), (int, float)):
                sample[key] = round(float(sample[key]) - pressure_drop, 2)

        if isinstance(sample.get("speedKph"), (int, float)):
            sample["speedKph"] = round(float(sample["speedKph"]) * (0.95 + (step * 0.002)), 2)

        if isinstance(sample.get("payloadTonnes"), (int, float)):
            sample["payloadTonnes"] = round(float(sample["payloadTonnes"]) * (0.97 + (step * 0.001)), 2)

        sample["ambientTemperatureC"] = round(27.5 + (step * 0.2), 2)
        sample["tireAgeHours"] = round(float(sample.get("tireAgeHours", 400.0)) + (step * 0.75), 2)
        return sample
