from app.domain.assets import AlertSeverity
from app.health.models import RuleEvaluation, RuleViolation


def evaluate_tire_temperature(measurements: dict[str, float | str | bool | None]) -> RuleEvaluation:
    tire_keys = ["frontLeftTireC", "frontRightTireC", "rearLeftTireC", "rearRightTireC"]
    temperatures = [
        float(measurements[key])
        for key in tire_keys
        if isinstance(measurements.get(key), (int, float))
    ]
    if not temperatures:
        return RuleEvaluation(penalty=0, violations=[])

    max_temp = max(temperatures)
    if max_temp >= 130:
        return RuleEvaluation(
            penalty=40,
            violations=[
                RuleViolation(
                    code="TIRE_TEMP_CRITICAL",
                    message=f"Tire temperature is critical at {max_temp:.1f}C",
                    severity=AlertSeverity.CRITICAL,
                    metric="tireTemperatureC",
                    value=max_temp,
                    threshold=130,
                )
            ],
        )

    if max_temp >= 110:
        return RuleEvaluation(
            penalty=18,
            violations=[
                RuleViolation(
                    code="TIRE_TEMP_HIGH",
                    message=f"Tire temperature is elevated at {max_temp:.1f}C",
                    severity=AlertSeverity.HIGH,
                    metric="tireTemperatureC",
                    value=max_temp,
                    threshold=110,
                )
            ],
        )

    return RuleEvaluation(penalty=0, violations=[])


def evaluate_tire_pressure(measurements: dict[str, float | str | bool | None]) -> RuleEvaluation:
    pressure_keys = ["frontLeftTirePsi", "frontRightTirePsi", "rearLeftTirePsi", "rearRightTirePsi"]
    pressures = [
        float(measurements[key])
        for key in pressure_keys
        if isinstance(measurements.get(key), (int, float))
    ]
    if not pressures:
        return RuleEvaluation(penalty=0, violations=[])

    min_pressure = min(pressures)
    max_pressure = max(pressures)

    if min_pressure < 85 or max_pressure > 125:
        return RuleEvaluation(
            penalty=24,
            violations=[
                RuleViolation(
                    code="TIRE_PRESSURE_CRITICAL",
                    message=f"Tire pressure is out of safe range ({min_pressure:.1f}-{max_pressure:.1f} psi)",
                    severity=AlertSeverity.CRITICAL,
                    metric="tirePressurePsi",
                    value=min_pressure if min_pressure < 85 else max_pressure,
                    threshold=85 if min_pressure < 85 else 125,
                )
            ],
        )

    if min_pressure < 95 or max_pressure > 115:
        return RuleEvaluation(
            penalty=12,
            violations=[
                RuleViolation(
                    code="TIRE_PRESSURE_WARNING",
                    message=f"Tire pressure drift detected ({min_pressure:.1f}-{max_pressure:.1f} psi)",
                    severity=AlertSeverity.MEDIUM,
                    metric="tirePressurePsi",
                    value=min_pressure if min_pressure < 95 else max_pressure,
                    threshold=95 if min_pressure < 95 else 115,
                )
            ],
        )

    return RuleEvaluation(penalty=0, violations=[])


def evaluate_payload(measurements: dict[str, float | str | bool | None]) -> RuleEvaluation:
    payload = measurements.get("payloadTonnes")
    capacity = measurements.get("payloadCapacityTonnes")
    if not isinstance(payload, (int, float)):
        return RuleEvaluation(penalty=0, violations=[])

    rated_capacity = float(capacity) if isinstance(capacity, (int, float)) else 220.0
    payload_ratio = float(payload) / rated_capacity

    if payload_ratio >= 1.10:
        return RuleEvaluation(
            penalty=26,
            violations=[
                RuleViolation(
                    code="PAYLOAD_CRITICAL",
                    message=f"Payload exceeds limit at {payload_ratio * 100:.1f}%",
                    severity=AlertSeverity.CRITICAL,
                    metric="payloadRatio",
                    value=payload_ratio * 100,
                    threshold=110,
                )
            ],
        )

    if payload_ratio >= 1.00:
        return RuleEvaluation(
            penalty=12,
            violations=[
                RuleViolation(
                    code="PAYLOAD_HIGH",
                    message=f"Payload is high at {payload_ratio * 100:.1f}%",
                    severity=AlertSeverity.HIGH,
                    metric="payloadRatio",
                    value=payload_ratio * 100,
                    threshold=100,
                )
            ],
        )

    return RuleEvaluation(penalty=0, violations=[])


def evaluate_speed(measurements: dict[str, float | str | bool | None]) -> RuleEvaluation:
    speed = measurements.get("speedKph")
    if not isinstance(speed, (int, float)):
        return RuleEvaluation(penalty=0, violations=[])

    speed_value = float(speed)
    if speed_value >= 60:
        return RuleEvaluation(
            penalty=24,
            violations=[
                RuleViolation(
                    code="SPEED_CRITICAL",
                    message=f"Speed exceeds safe operating limit at {speed_value:.1f} km/h",
                    severity=AlertSeverity.CRITICAL,
                    metric="speedKph",
                    value=speed_value,
                    threshold=60,
                )
            ],
        )

    if speed_value >= 45:
        return RuleEvaluation(
            penalty=10,
            violations=[
                RuleViolation(
                    code="SPEED_WARNING",
                    message=f"Speed is above recommended band at {speed_value:.1f} km/h",
                    severity=AlertSeverity.MEDIUM,
                    metric="speedKph",
                    value=speed_value,
                    threshold=45,
                )
            ],
        )

    return RuleEvaluation(penalty=0, violations=[])
