from app.prediction.models import PredictionEventType


EVENT_THRESHOLDS: dict[PredictionEventType, dict[str, float]] = {
    PredictionEventType.TIRE_OVERHEAT: {"warning": 110.0, "critical": 130.0},
    PredictionEventType.TIRE_BLOWOUT: {"warning": 90.0, "critical": 85.0},
    PredictionEventType.ENGINE_OVERHEAT: {"warning": 100.0, "critical": 112.0},
}


def max_tire_temperature(measurements: dict[str, float | str | bool | None]) -> float | None:
    keys = ["frontLeftTireC", "frontRightTireC", "rearLeftTireC", "rearRightTireC"]
    values = [float(measurements[key]) for key in keys if isinstance(measurements.get(key), (int, float))]
    return max(values) if values else None


def min_tire_pressure(measurements: dict[str, float | str | bool | None]) -> float | None:
    keys = ["frontLeftTirePsi", "frontRightTirePsi", "rearLeftTirePsi", "rearRightTirePsi"]
    values = [float(measurements[key]) for key in keys if isinstance(measurements.get(key), (int, float))]
    return min(values) if values else None
