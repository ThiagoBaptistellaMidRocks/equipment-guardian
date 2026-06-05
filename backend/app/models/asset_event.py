from enum import StrEnum

from pydantic import BaseModel


class AssetEventType(StrEnum):
    TIRE_OVERHEAT = "TIRE_OVERHEAT"
    TIRE_FAILURE = "TIRE_FAILURE"
    ENGINE_OVERHEAT = "ENGINE_OVERHEAT"
    BRAKE_FAILURE = "BRAKE_FAILURE"


class AssetEventSeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AssetEvent(BaseModel):
    asset_id: str
    event_type: AssetEventType
    event_time: str
    severity: AssetEventSeverity
