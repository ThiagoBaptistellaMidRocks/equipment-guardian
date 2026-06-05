from enum import StrEnum

from pydantic import BaseModel

from app.domain.assets import AssetType


class PredictionEventType(StrEnum):
    TIRE_OVERHEAT = "TIRE_OVERHEAT"
    TIRE_BLOWOUT = "TIRE_BLOWOUT"
    ENGINE_OVERHEAT = "ENGINE_OVERHEAT"


class PredictionInput(BaseModel):
    assetId: str
    assetType: AssetType
    currentTelemetry: dict[str, float | str | bool | None]
    historicalTelemetry: list[dict[str, float | str | bool | None]]


class Prediction(BaseModel):
    assetId: str
    assetType: AssetType
    eventType: PredictionEventType
    confidence: float
    timeToEventMinutes: int
    recommendedAction: str
