from collections.abc import Sequence
from datetime import datetime

import pandas as pd

from app.domain.assets import AssetTelemetry
from app.ml.feature_builder import FeatureBuilder
from app.models.asset_event import AssetEvent, AssetEventType


class DatasetBuilder:
    def __init__(self, feature_builder: FeatureBuilder | None = None) -> None:
        self._feature_builder = feature_builder or FeatureBuilder()

    def build_dataset(self, telemetry_history: Sequence[AssetTelemetry], asset_events: Sequence[AssetEvent]) -> pd.DataFrame:
        rows: list[dict[str, float | int]] = []
        events_by_asset = self._group_events(asset_events)
        telemetry_by_asset = self._group_telemetry(telemetry_history)

        for asset_id, samples in telemetry_by_asset.items():
            events = events_by_asset.get(asset_id, [])
            ordered_samples = sorted(samples, key=lambda item: item.recordedAt)

            for index, sample in enumerate(ordered_samples):
                current_window = ordered_samples[: index + 1]
                features = self._feature_builder.build_features(current_window)
                rows.append({**features, "event": self._label_event(sample.recordedAt, events)})

        return pd.DataFrame(rows)

    def _label_event(self, telemetry_time: str, events: Sequence[AssetEvent]) -> int:
        telemetry_timestamp = datetime.fromisoformat(telemetry_time.replace("Z", "+00:00"))
        if any(
            event.event_type in {AssetEventType.TIRE_OVERHEAT, AssetEventType.TIRE_FAILURE}
            and datetime.fromisoformat(event.event_time.replace("Z", "+00:00")) >= telemetry_timestamp
            for event in events
        ):
            return 1

        return 0

    def _group_telemetry(self, telemetry_history: Sequence[AssetTelemetry]) -> dict[str, list[AssetTelemetry]]:
        grouped: dict[str, list[AssetTelemetry]] = {}
        for sample in telemetry_history:
            grouped.setdefault(sample.assetId, []).append(sample)
        return grouped

    def _group_events(self, asset_events: Sequence[AssetEvent]) -> dict[str, list[AssetEvent]]:
        grouped: dict[str, list[AssetEvent]] = {}
        for event in asset_events:
            grouped.setdefault(event.asset_id, []).append(event)
        return grouped
