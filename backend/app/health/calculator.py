from app.domain.assets import Asset, AssetHealth, AssetTelemetry, AssetType, RiskLevel
from app.health.rules import (
    evaluate_payload,
    evaluate_speed,
    evaluate_tire_pressure,
    evaluate_tire_temperature,
)


class HealthCalculator:
    def calculate(self, asset: Asset, telemetry: AssetTelemetry) -> AssetHealth:
        if asset.assetType != AssetType.HAUL_TRUCK:
            return AssetHealth(
                assetId=asset.id,
                assetType=asset.assetType,
                observedAt=telemetry.recordedAt,
                healthScore=100,
                riskLevel=RiskLevel.LOW,
                activeAlerts=[],
            )

        measurements = telemetry.measurements
        evaluations = [
            evaluate_tire_temperature(measurements),
            evaluate_tire_pressure(measurements),
            evaluate_payload(measurements),
            evaluate_speed(measurements),
        ]

        total_penalty = sum(evaluation.penalty for evaluation in evaluations)
        health_score = max(0, min(100, 100 - total_penalty))
        active_alerts = [
            violation.to_active_alert()
            for evaluation in evaluations
            for violation in evaluation.violations
        ]

        return AssetHealth(
            assetId=asset.id,
            assetType=asset.assetType,
            observedAt=telemetry.recordedAt,
            healthScore=health_score,
            riskLevel=self._risk_level(health_score, active_alerts),
            activeAlerts=active_alerts,
        )

    def _risk_level(self, health_score: int, active_alerts: list) -> RiskLevel:
        has_critical = any(alert.severity == "CRITICAL" for alert in active_alerts)
        has_high = any(alert.severity == "HIGH" for alert in active_alerts)

        if has_critical or health_score < 40:
            return RiskLevel.CRITICAL

        if has_high or health_score < 65:
            return RiskLevel.HIGH

        if active_alerts or health_score < 80:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW
