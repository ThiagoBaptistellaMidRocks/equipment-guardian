from app.prediction.events import EVENT_THRESHOLDS, max_tire_temperature, min_tire_pressure
from app.prediction.models import Prediction, PredictionEventType, PredictionInput
from app.prediction.recommendations import recommended_action


class TrendPredictor:
    def predict(self, prediction_input: PredictionInput) -> Prediction | None:
        if prediction_input.assetType != "HAUL_TRUCK":
            return None

        candidates = [
            self._predict_tire_overheat(prediction_input),
            self._predict_tire_blowout(prediction_input),
            self._predict_engine_overheat(prediction_input),
        ]
        predictions = [candidate for candidate in candidates if candidate is not None]
        if not predictions:
            return None

        return sorted(predictions, key=lambda item: (item.confidence, -item.timeToEventMinutes), reverse=True)[0]

    def _predict_tire_overheat(self, prediction_input: PredictionInput) -> Prediction | None:
        current = max_tire_temperature(prediction_input.currentTelemetry)
        if current is None:
            return None

        history_values = [
            value
            for sample in prediction_input.historicalTelemetry
            for value in [max_tire_temperature(sample)]
            if value is not None
        ]
        if len(history_values) < 2:
            return None

        slope = self._slope(history_values)
        if slope <= 0.05 and current < EVENT_THRESHOLDS[PredictionEventType.TIRE_OVERHEAT]["warning"]:
            return None

        threshold = EVENT_THRESHOLDS[PredictionEventType.TIRE_OVERHEAT]["critical"]
        eta = self._estimate_minutes(current, slope, threshold, fallback=60)
        confidence = self._confidence(current=current, slope=slope, warning=110.0, critical=130.0)
        return Prediction(
            assetId=prediction_input.assetId,
            assetType=prediction_input.assetType,
            eventType=PredictionEventType.TIRE_OVERHEAT,
            confidence=confidence,
            timeToEventMinutes=eta,
            recommendedAction=recommended_action(PredictionEventType.TIRE_OVERHEAT),
        )

    def _predict_tire_blowout(self, prediction_input: PredictionInput) -> Prediction | None:
        current = min_tire_pressure(prediction_input.currentTelemetry)
        if current is None:
            return None

        history_values = [
            value
            for sample in prediction_input.historicalTelemetry
            for value in [min_tire_pressure(sample)]
            if value is not None
        ]
        if len(history_values) < 2:
            return None

        slope = self._slope(history_values)
        if slope >= -0.03 and current > EVENT_THRESHOLDS[PredictionEventType.TIRE_BLOWOUT]["warning"]:
            return None

        threshold = EVENT_THRESHOLDS[PredictionEventType.TIRE_BLOWOUT]["critical"]
        eta = self._estimate_minutes(current, slope, threshold, fallback=90)
        confidence = self._confidence(current=125.0 - current, slope=abs(slope), warning=30.0, critical=40.0)
        return Prediction(
            assetId=prediction_input.assetId,
            assetType=prediction_input.assetType,
            eventType=PredictionEventType.TIRE_BLOWOUT,
            confidence=confidence,
            timeToEventMinutes=eta,
            recommendedAction=recommended_action(PredictionEventType.TIRE_BLOWOUT),
        )

    def _predict_engine_overheat(self, prediction_input: PredictionInput) -> Prediction | None:
        current_value = prediction_input.currentTelemetry.get("engineTempC")
        if not isinstance(current_value, (int, float)):
            return None

        history_values = [
            float(sample["engineTempC"])
            for sample in prediction_input.historicalTelemetry
            if isinstance(sample.get("engineTempC"), (int, float))
        ]
        if len(history_values) < 2:
            return None

        current = float(current_value)
        slope = self._slope(history_values)
        if slope <= 0.03 and current < EVENT_THRESHOLDS[PredictionEventType.ENGINE_OVERHEAT]["warning"]:
            return None

        threshold = EVENT_THRESHOLDS[PredictionEventType.ENGINE_OVERHEAT]["critical"]
        eta = self._estimate_minutes(current, slope, threshold, fallback=120)
        confidence = self._confidence(current=current, slope=slope, warning=100.0, critical=112.0)
        return Prediction(
            assetId=prediction_input.assetId,
            assetType=prediction_input.assetType,
            eventType=PredictionEventType.ENGINE_OVERHEAT,
            confidence=confidence,
            timeToEventMinutes=eta,
            recommendedAction=recommended_action(PredictionEventType.ENGINE_OVERHEAT),
        )

    def _slope(self, values: list[float]) -> float:
        return (values[-1] - values[0]) / max(len(values) - 1, 1)

    def _estimate_minutes(self, current: float, slope: float, threshold: float, fallback: int) -> int:
        if slope == 0:
            return fallback

        minutes = int((threshold - current) / slope) if slope > 0 else int((current - threshold) / abs(slope))
        return max(5, min(180, minutes)) if minutes > 0 else 5

    def _confidence(self, current: float, slope: float, warning: float, critical: float) -> float:
        proximity = max(0.0, min(1.0, (current - warning) / max(critical - warning, 1.0)))
        trend_strength = max(0.0, min(1.0, abs(slope) / 2.0))
        return round(min(0.99, 0.45 + (0.35 * proximity) + (0.20 * trend_strength)), 2)
