export type AssetType = "HAUL_TRUCK" | "EXCAVATOR" | "DRILL";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type AlertSeverity = "MEDIUM" | "HIGH" | "CRITICAL";

export type PredictionEventType = "TIRE_OVERHEAT" | "TIRE_BLOWOUT" | "ENGINE_OVERHEAT";

export interface AssetPosition {
  x: number;
  y: number;
  z: number;
}

export interface Asset {
  id: string;
  name: string;
  assetType: AssetType;
  siteId: string;
  manufacturer: string;
  model: string;
  position: AssetPosition;
}

export interface AssetHealth {
  assetId: string;
  assetType: AssetType;
  observedAt: string;
  healthScore: number;
  riskLevel: RiskLevel;
  activeAlerts: ActiveAlert[];
}

export interface ActiveAlert {
  code: string;
  message: string;
  severity: AlertSeverity;
  metric: string;
  value: number;
  threshold: number;
}

export interface AssetAlert extends ActiveAlert {
  assetId: string;
  assetName: string;
  assetType: AssetType;
  riskLevel: RiskLevel;
}

export interface AssetTelemetry {
  assetId: string;
  recordedAt: string;
  source: string;
  measurements: Record<string, number | string | boolean | null>;
}

export interface AssetOverview {
  asset: Asset;
  health: AssetHealth;
  telemetry: AssetTelemetry;
}

export interface Prediction {
  assetId: string;
  assetType: AssetType;
  eventType: PredictionEventType;
  confidence: number;
  timeToEventMinutes: number;
  recommendedAction: string;
}
