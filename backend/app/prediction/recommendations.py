from app.prediction.models import PredictionEventType


RECOMMENDED_ACTIONS: dict[PredictionEventType, str] = {
    PredictionEventType.TIRE_OVERHEAT: "Reduce speed, dispatch tire crew, and move asset to cooling lane.",
    PredictionEventType.TIRE_BLOWOUT: "Stop asset, isolate lane, and replace tire before next haul cycle.",
    PredictionEventType.ENGINE_OVERHEAT: "Reduce load, inspect cooling circuit, and schedule immediate maintenance.",
}


def recommended_action(event_type: PredictionEventType) -> str:
    return RECOMMENDED_ACTIONS[event_type]
