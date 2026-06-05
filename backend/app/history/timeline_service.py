from pydantic import BaseModel

from app.domain.assets import AssetIncident, AssetOverview, IncidentSeverity
from app.health.engine import health_engine
from app.history.event_history import EventHistoryItem, TimelineEntryType
from app.history.telemetry_history import telemetry_history_store
from app.models.prediction_service import PredictionService
from app.prediction.engine import prediction_engine
from app.repositories.mock_asset_repository import mock_asset_repository


class PredictionExplanation(BaseModel):
    topPredictionDrivers: list[str]
    supportingTelemetryValues: dict[str, float]


class AssetHistoryResponse(BaseModel):
    assetId: str
    telemetry: list[dict[str, float | str | bool | None]]
    predictionExplanation: PredictionExplanation


class AssetTimelineResponse(BaseModel):
    assetId: str
    timeline: list[EventHistoryItem]


class TimelineService:
    def __init__(self, ml_prediction_service: PredictionService | None = None) -> None:
        self._ml_prediction_service = ml_prediction_service or PredictionService()

    def get_asset_history(self, asset_id: str) -> AssetHistoryResponse | None:
        asset = mock_asset_repository.get_asset(asset_id)
        if asset is None:
            return None

        history = telemetry_history_store.list_asset_history(asset_id)
        explanation = self._prediction_explanation(asset, history)

        return AssetHistoryResponse(
            assetId=asset_id,
            telemetry=[sample.measurements for sample in history],
            predictionExplanation=explanation,
        )

    def get_asset_timeline(self, asset_id: str) -> AssetTimelineResponse | None:
        asset = mock_asset_repository.get_asset(asset_id)
        if asset is None:
            return None

        history = telemetry_history_store.list_asset_history(asset_id)
        timeline: list[EventHistoryItem] = []

        timeline.extend(self._telemetry_events(asset_id, history))
        timeline.extend(self._alert_events(asset))
        timeline.extend(self._health_change_events(asset, history))
        timeline.extend(self._prediction_events(asset))
        timeline.extend(self._incident_events(asset))

        return AssetTimelineResponse(
            assetId=asset_id,
            timeline=sorted(timeline, key=lambda item: item.timestamp, reverse=True),
        )

    def _telemetry_events(self, asset_id: str, history) -> list[EventHistoryItem]:
        if not history:
            return []

        sampled = history[::8][-5:]
        events: list[EventHistoryItem] = []
        for sample in sampled:
            speed = sample.measurements.get("speedKph", 0)
            payload = sample.measurements.get("payloadTonnes", 0)
            events.append(
                EventHistoryItem(
                    assetId=asset_id,
                    timestamp=sample.recordedAt,
                    entryType=TimelineEntryType.TELEMETRY_EVENT,
                    message=f"Telemetry snapshot: speed {speed} km/h, payload {payload} t",
                    severity="LOW",
                    details={
                        "speedKph": speed,
                        "payloadTonnes": payload,
                    },
                )
            )

        return events

    def _alert_events(self, asset: AssetOverview) -> list[EventHistoryItem]:
        return [
            EventHistoryItem(
                assetId=asset.asset.id,
                timestamp=asset.health.observedAt,
                entryType=TimelineEntryType.ALERT,
                message=alert.message,
                severity=alert.severity,
                details={
                    "metric": alert.metric,
                    "value": alert.value,
                    "threshold": alert.threshold,
                },
            )
            for alert in asset.health.activeAlerts
        ]

    def _health_change_events(self, asset: AssetOverview, history) -> list[EventHistoryItem]:
        if len(history) < 2:
            return []

        first = history[0]
        midpoint = history[len(history) // 2]
        last = history[-1]

        snapshots = []
        for telemetry in [first, midpoint, last]:
            historical_overview = AssetOverview(asset=asset.asset, telemetry=telemetry, health=asset.health)
            computed_health = health_engine.evaluate_asset(historical_overview)
            snapshots.append((telemetry.recordedAt, computed_health.healthScore, computed_health.riskLevel))

        return [
            EventHistoryItem(
                assetId=asset.asset.id,
                timestamp=timestamp,
                entryType=TimelineEntryType.HEALTH_CHANGE,
                message=f"Health moved to {risk_level} with score {score}",
                severity=risk_level,
                details={"healthScore": score, "riskLevel": risk_level},
            )
            for timestamp, score, risk_level in snapshots
        ]

    def _prediction_events(self, asset: AssetOverview) -> list[EventHistoryItem]:
        events: list[EventHistoryItem] = []
        rule_prediction = prediction_engine.predict_asset(asset)
        if rule_prediction is not None:
            events.append(
                EventHistoryItem(
                    assetId=asset.asset.id,
                    timestamp=asset.telemetry.recordedAt,
                    entryType=TimelineEntryType.PREDICTION,
                    message=f"Rule prediction: {rule_prediction.eventType}",
                    severity=str(round(rule_prediction.confidence * 100)),
                    details={
                        "confidence": round(rule_prediction.confidence * 100),
                        "timeToEventMinutes": rule_prediction.timeToEventMinutes,
                    },
                )
            )

        ml_prediction = self._ml_prediction_service.predict_asset(asset)
        if ml_prediction is not None:
            events.append(
                EventHistoryItem(
                    assetId=asset.asset.id,
                    timestamp=asset.telemetry.recordedAt,
                    entryType=TimelineEntryType.PREDICTION,
                    message=f"ML prediction: {ml_prediction.predictedEvent}",
                    severity=str(ml_prediction.confidence),
                    details={
                        "probability": ml_prediction.probability,
                        "confidence": ml_prediction.confidence,
                        "modelVersion": ml_prediction.modelVersion,
                    },
                )
            )

        return events

    def _incident_events(self, asset: AssetOverview) -> list[EventHistoryItem]:
        incidents: list[AssetIncident] = []
        if asset.health.riskLevel in {"HIGH", "CRITICAL"}:
            incidents.append(
                AssetIncident(
                    assetId=asset.asset.id,
                    eventType="TIRE_OVERHEAT",
                    eventTime=asset.telemetry.recordedAt,
                    severity=IncidentSeverity.CRITICAL if asset.health.riskLevel == "CRITICAL" else IncidentSeverity.HIGH,
                    summary="Risk profile indicates high probability of tire incident.",
                )
            )

        return [
            EventHistoryItem(
                assetId=incident.assetId,
                timestamp=incident.eventTime,
                entryType=TimelineEntryType.INCIDENT,
                message=incident.summary,
                severity=incident.severity,
                details={"eventType": incident.eventType},
            )
            for incident in incidents
        ]

    def _prediction_explanation(self, asset: AssetOverview, history) -> PredictionExplanation:
        latest = history[-1] if history else asset.telemetry
        measurements = latest.measurements
        max_tire_temp = max(
            [
                float(measurements[key])
                for key in ("frontLeftTireC", "frontRightTireC", "rearLeftTireC", "rearRightTireC")
                if isinstance(measurements.get(key), (int, float))
            ]
            or [0.0]
        )
        min_tire_pressure = min(
            [
                float(measurements[key])
                for key in ("frontLeftTirePsi", "frontRightTirePsi", "rearLeftTirePsi", "rearRightTirePsi")
                if isinstance(measurements.get(key), (int, float))
            ]
            or [0.0]
        )

        drivers = [
            "Rising 15-minute tire temperature trend",
            "Low tire pressure spread across rear axle",
            "Payload and speed combination increasing heat load",
        ]

        return PredictionExplanation(
            topPredictionDrivers=drivers,
            supportingTelemetryValues={
                "maxTireTempC": round(max_tire_temp, 2),
                "minTirePressurePsi": round(min_tire_pressure, 2),
                "payloadTonnes": float(measurements.get("payloadTonnes", 0) or 0),
                "speedKph": float(measurements.get("speedKph", 0) or 0),
            },
        )


timeline_service = TimelineService()
