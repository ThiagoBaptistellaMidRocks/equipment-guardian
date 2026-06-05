from datetime import datetime, timedelta, timezone

from app.domain.assets import AssetTelemetry
from app.repositories.mock_asset_repository import mock_asset_repository


class TelemetryHistoryStore:
    def __init__(self) -> None:
        self._history_by_asset = self._build_history()

    def list_asset_history(self, asset_id: str) -> list[AssetTelemetry]:
        return self._history_by_asset.get(asset_id, [])

    def list_all_history(self) -> dict[str, list[AssetTelemetry]]:
        return self._history_by_asset

    def _build_history(self) -> dict[str, list[AssetTelemetry]]:
        history: dict[str, list[AssetTelemetry]] = {}

        for overview in mock_asset_repository.list_assets():
            history[overview.asset.id] = self._generate_asset_history(overview.telemetry)

        return history

    def _generate_asset_history(self, current: AssetTelemetry) -> list[AssetTelemetry]:
        baseline = dict(current.measurements)
        current_time = datetime.fromisoformat(current.recordedAt.replace("Z", "+00:00"))
        samples: list[AssetTelemetry] = []

        for index in range(36):
            step = 35 - index
            sample_time = current_time - timedelta(minutes=step * 5)
            trend = 0.84 + (index * 0.005)
            sample_measurements = self._sample_measurements(baseline, trend, index)
            samples.append(
                AssetTelemetry(
                    assetId=current.assetId,
                    recordedAt=sample_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                    source="telemetry-history",
                    measurements=sample_measurements,
                )
            )

        return samples

    def _sample_measurements(
        self,
        measurements: dict[str, float | str | bool | None],
        trend: float,
        index: int,
    ) -> dict[str, float | str | bool | None]:
        sample = dict(measurements)

        for key, value in sample.items():
            if isinstance(value, (int, float)):
                if "Psi" in key:
                    sample[key] = round(float(value) + (1 - trend) * 6, 2)
                elif "Temp" in key or key.endswith("C"):
                    sample[key] = round(float(value) * trend, 2)
                elif key == "tireAgeHours":
                    sample[key] = round(float(value) - max((36 - index) * 0.75, 0), 2)
                else:
                    sample[key] = round(float(value) * (0.9 + (index * 0.0025)), 2)

        return sample


telemetry_history_store = TelemetryHistoryStore()
