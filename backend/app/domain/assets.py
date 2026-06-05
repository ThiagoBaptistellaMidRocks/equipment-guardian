from enum import StrEnum

from pydantic import BaseModel


class AssetType(StrEnum):
    HAUL_TRUCK = "HAUL_TRUCK"
    EXCAVATOR = "EXCAVATOR"
    DRILL = "DRILL"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertSeverity(StrEnum):
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AssetPosition(BaseModel):
    x: float
    y: float
    z: float = 0


class Asset(BaseModel):
    id: str
    name: str
    assetType: AssetType
    siteId: str
    manufacturer: str
    model: str
    position: AssetPosition


class ActiveAlert(BaseModel):
    code: str
    message: str
    severity: AlertSeverity
    metric: str
    value: float
    threshold: float


class AssetHealth(BaseModel):
    assetId: str
    assetType: AssetType
    observedAt: str
    healthScore: int
    riskLevel: RiskLevel
    activeAlerts: list[ActiveAlert]


class AssetTelemetry(BaseModel):
    assetId: str
    recordedAt: str
    source: str
    measurements: dict[str, float | str | bool | None]


class AssetOverview(BaseModel):
    asset: Asset
    health: AssetHealth
    telemetry: AssetTelemetry
