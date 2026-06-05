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

export interface MlPrediction {
  assetId: string;
  predictedEvent: PredictionEventType;
  probability: number;
  confidence: number;
  modelVersion: string;
}

export type TimelineEntryType = "TELEMETRY_EVENT" | "ALERT" | "HEALTH_CHANGE" | "PREDICTION" | "INCIDENT";

export interface PredictionExplanation {
  topPredictionDrivers: string[];
  supportingTelemetryValues: Record<string, number>;
}

export interface AssetHistory {
  assetId: string;
  telemetry: Array<Record<string, number | string | boolean | null>>;
  predictionExplanation: PredictionExplanation;
}

export interface TimelineEntry {
  assetId: string;
  timestamp: string;
  entryType: TimelineEntryType;
  message: string;
  severity: string;
  details: Record<string, number | string | boolean | null>;
}

export interface AssetTimeline {
  assetId: string;
  timeline: TimelineEntry[];
}

export interface TrendPoint {
  timestamp: string;
  value: number;
}

export interface FleetAnalytics {
  failureTrends: TrendPoint[];
  fleetHealthTrends: TrendPoint[];
  predictedFailures: number;
  downtimeAvoided: number;
  assetsWithHighestRisk: string[];
  averagePredictionConfidence: number;
}
