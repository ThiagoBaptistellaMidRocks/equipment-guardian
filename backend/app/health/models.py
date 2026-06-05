from pydantic import BaseModel

from app.domain.assets import ActiveAlert, AlertSeverity, AssetType, RiskLevel


class RuleViolation(BaseModel):
    code: str
    message: str
    severity: AlertSeverity
    metric: str
    value: float
    threshold: float

    def to_active_alert(self) -> ActiveAlert:
        return ActiveAlert(
            code=self.code,
            message=self.message,
            severity=self.severity,
            metric=self.metric,
            value=self.value,
            threshold=self.threshold,
        )


class RuleEvaluation(BaseModel):
    penalty: int
    violations: list[RuleViolation]


class AssetAlert(BaseModel):
    assetId: str
    assetName: str
    assetType: AssetType
    riskLevel: RiskLevel
    code: str
    message: str
    severity: AlertSeverity
    metric: str
    value: float
    threshold: float
