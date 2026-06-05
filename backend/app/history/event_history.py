from enum import StrEnum

from pydantic import BaseModel


class TimelineEntryType(StrEnum):
    TELEMETRY_EVENT = "TELEMETRY_EVENT"
    ALERT = "ALERT"
    HEALTH_CHANGE = "HEALTH_CHANGE"
    PREDICTION = "PREDICTION"
    INCIDENT = "INCIDENT"


class EventHistoryItem(BaseModel):
    assetId: str
    timestamp: str
    entryType: TimelineEntryType
    message: str
    severity: str
    details: dict[str, float | str | bool | None]
