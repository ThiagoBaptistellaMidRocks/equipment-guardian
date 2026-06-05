import type { AssetPosition, AssetType, RiskLevel } from "../types/assets";

export function formatAssetType(assetType: AssetType): string {
  return assetType
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatTelemetryLabel(key: string): string {
  return key.replace(/([A-Z])/g, " $1").replace(/^./, (match) => match.toUpperCase());
}

export function healthTone(riskLevel: RiskLevel): "normal" | "warning" | "critical" {
  if (riskLevel === "CRITICAL") {
    return "critical";
  }

  if (riskLevel === "HIGH" || riskLevel === "MEDIUM") {
    return "warning";
  }

  return "normal";
}

export function assetIcon(assetType: AssetType): string {
  if (assetType === "HAUL_TRUCK") {
    return "▣";
  }

  if (assetType === "EXCAVATOR") {
    return "×";
  }

  return "◉";
}

export function mapPositionToPercent(position: AssetPosition): { left: number; top: number } {
  return {
    left: ((position.x + 60) / 120) * 100,
    top: ((45 - position.y) / 90) * 100
  };
}

export function measurementNumber(
  measurements: Record<string, number | string | boolean | null>,
  key: string,
  fallback = 0
): number {
  const value = measurements[key];
  return typeof value === "number" ? value : fallback;
}

export function measurementText(
  measurements: Record<string, number | string | boolean | null>,
  key: string,
  fallback = "-"
): string {
  const value = measurements[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : fallback;
}
