from collections.abc import Sequence
from datetime import datetime

from app.domain.assets import AssetTelemetry


class FeatureBuilder:
    feature_names = [
        "avg_temp_5m",
        "avg_temp_15m",
        "max_temp_15m",
        "temp_rise_rate",
        "payload_tonnes",
        "speed_kmh",
        "ambient_temperature",
        "tire_pressure",
        "tire_age_hours",
    ]

    def build_features(self, telemetry_history: Sequence[AssetTelemetry]) -> dict[str, float]:
        history = sorted(telemetry_history, key=lambda item: item.recordedAt)
        if not history:
            return {name: 0.0 for name in self.feature_names}

        latest = history[-1]
        latest_time = self._parse_time(latest.recordedAt)
        temperatures = [self._sample_temperature(point) for point in history]

        temp_5m = self._window_values(history, latest_time, 5)
        temp_15m = self._window_values(history, latest_time, 15)

        payload = self._measurement_number(latest.measurements, "payloadTonnes", 0.0)
        speed = self._measurement_number(latest.measurements, "speedKph", 0.0)
        ambient = self._measurement_number(latest.measurements, "ambientTemperatureC", 28.0)
        tire_pressure = self._sample_pressure(latest)
        tire_age_hours = self._measurement_number(latest.measurements, "tireAgeHours", 0.0)

        earliest_temp = temperatures[0]
        latest_temp = temperatures[-1]
        duration_minutes = max((latest_time - self._parse_time(history[0].recordedAt)).total_seconds() / 60.0, 1.0)

        return {
            "avg_temp_5m": self._average(temp_5m),
            "avg_temp_15m": self._average(temp_15m),
            "max_temp_15m": max(temp_15m) if temp_15m else latest_temp,
            "temp_rise_rate": (latest_temp - earliest_temp) / duration_minutes,
            "payload_tonnes": payload,
            "speed_kmh": speed,
            "ambient_temperature": ambient,
            "tire_pressure": tire_pressure,
            "tire_age_hours": tire_age_hours,
        }

    def vectorize(self, features: dict[str, float]) -> list[float]:
        return [features[name] for name in self.feature_names]

    def _window_values(self, history: Sequence[AssetTelemetry], latest_time: datetime, window_minutes: int) -> list[float]:
        window_start = latest_time.timestamp() - (window_minutes * 60)
        values = []
        for point in history:
            point_time = self._parse_time(point.recordedAt).timestamp()
            if point_time >= window_start:
                values.append(self._sample_temperature(point))
        return values or [self._sample_temperature(history[-1])]

    def _sample_temperature(self, telemetry: AssetTelemetry) -> float:
        values = [
            self._measurement_number(telemetry.measurements, key, 0.0)
            for key in ("frontLeftTireC", "frontRightTireC", "rearLeftTireC", "rearRightTireC")
            if isinstance(telemetry.measurements.get(key), (int, float))
        ]
        if values:
            return sum(values) / len(values)
        return self._measurement_number(telemetry.measurements, "engineTempC", 0.0)

    def _sample_pressure(self, telemetry: AssetTelemetry) -> float:
        values = [
            self._measurement_number(telemetry.measurements, key, 0.0)
            for key in ("frontLeftTirePsi", "frontRightTirePsi", "rearLeftTirePsi", "rearRightTirePsi")
            if isinstance(telemetry.measurements.get(key), (int, float))
        ]
        return sum(values) / len(values) if values else 0.0

    def _average(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _measurement_number(self, measurements: dict[str, float | str | bool | None], key: str, fallback: float) -> float:
        value = measurements.get(key)
        return float(value) if isinstance(value, (int, float)) else fallback

    def _parse_time(self, timestamp: str) -> datetime:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
