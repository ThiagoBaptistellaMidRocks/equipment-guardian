import { AlertTriangle, ArrowLeft, Truck, X } from "lucide-react";
import { useEffect, useState, type CSSProperties } from "react";
import { useAssetHistory, useAssetTimeline, useMlPrediction, usePrediction } from "../hooks/useAssets";
import type { AssetOverview } from "../types/assets";
import { formatAssetType, healthTone, measurementNumber, measurementText } from "../utils/assets";

interface AssetDrawerProps {
  assetOverview: AssetOverview | null;
  isLoading: boolean;
  onClose: () => void;
}

function DetailCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail-cell">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MetricCard({ label, value, note, tone }: { label: string; value: string; note: string; tone?: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong className={tone}>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function TireGauge({ label, value, tone }: { label: string; value: number; tone: "good" | "warning" | "critical" }) {
  return (
    <div className={`tire-gauge ${tone}`}>
      <div className="gauge-arc" style={{ "--gauge-value": `${Math.min(value / 220, 1) * 180}deg` } as CSSProperties}>
        <strong>{value}</strong>
      </div>
      <span>{label}</span>
    </div>
  );
}

function HealthOverview({ assetOverview }: { assetOverview: AssetOverview }) {
  const measurements = assetOverview.telemetry.measurements;
  const tireLoad = measurementNumber(measurements, "tireLoadPercent", 68);
  const usefulLife = measurementNumber(measurements, "usefulLifeHours", 24);
  const tone = healthTone(assetOverview.health.riskLevel);

  return (
    <section className="drawer-section">
      <h3>Health Overview</h3>
      <div className="metric-grid">
        <MetricCard label="Health Score" value={String(assetOverview.health.healthScore)} note="Calculated from rule engine" tone={tone} />
        <MetricCard label="Risk Level" value={assetOverview.health.riskLevel} note="Current operational risk" tone={tone} />
        <MetricCard label="Active Alerts" value={String(assetOverview.health.activeAlerts.length)} note="Triggered health rules" tone={tone} />
        <MetricCard label="Tire Load" value={`${tireLoad}%`} note="Above nominal" tone="warning" />
        <MetricCard label="Useful Life" value={`${usefulLife}h`} note="Until service" tone={tone} />
      </div>
    </section>
  );
}

function TireMonitor({ assetOverview }: { assetOverview: AssetOverview }) {
  const measurements = assetOverview.telemetry.measurements;
  const tires = [
    { label: "FL - Normal", value: measurementNumber(measurements, "frontLeftTireC", 94), tone: "good" as const },
    { label: "FR - Warning", value: measurementNumber(measurements, "frontRightTireC", 102), tone: "warning" as const },
    { label: "RL - Critical", value: measurementNumber(measurements, "rearLeftTireC", 187), tone: "critical" as const },
    { label: "RR - Warning", value: measurementNumber(measurements, "rearRightTireC", 141), tone: "warning" as const }
  ];

  return (
    <section className="drawer-section">
      <div className="section-heading">
        <h3>Tire Monitor</h3>
        <span>Live</span>
      </div>
      <div className="tire-grid">
        {tires.map((tire) => (
          <TireGauge key={tire.label} {...tire} />
        ))}
      </div>
    </section>
  );
}

function RiskInsight({ assetOverview }: { assetOverview: AssetOverview }) {
  const isCritical = assetOverview.health.riskLevel === "CRITICAL";
  const primaryAlert = assetOverview.health.activeAlerts[0];

  return (
    <section className="drawer-section">
      <h3>Health Risk Insight</h3>
      <article className="risk-card">
        <div className="risk-card-title">
          <strong>{primaryAlert?.message ?? "No active critical risk"}</strong>
          <span>{assetOverview.health.riskLevel}</span>
        </div>
        <div className="risk-stats">
          <div><small>Health Score</small><b>{assetOverview.health.healthScore}</b></div>
          <div><small>Active Alerts</small><b>{assetOverview.health.activeAlerts.length}</b></div>
          <div><small>Top Metric</small><b>{primaryAlert?.metric ?? "none"}</b></div>
          <div><small>Alert Severity</small><b>{primaryAlert?.severity ?? "none"}</b></div>
        </div>
        <div className="risk-progress"><span style={{ width: isCritical ? "84%" : "22%" }} /></div>
      </article>
    </section>
  );
}

function RecommendedActions({ assetOverview, isCritical }: { assetOverview: AssetOverview; isCritical: boolean }) {
  return (
    <section className="drawer-section">
      <h3>Recommended Actions</h3>
      <ul className="action-list">
        <li><AlertTriangle size={15} /><span>{isCritical ? "Halt truck immediately" : "Continue monitoring"}</span><b>{isCritical ? "Critical" : "Normal"}</b></li>
        {assetOverview.health.activeAlerts.slice(0, 2).map((alert) => (
          <li key={alert.code}><AlertTriangle size={15} /><span>{alert.message}</span><b>{alert.severity}</b></li>
        ))}
      </ul>
      <div className="drawer-actions">
        <button className="primary-action" type="button">Dispatch Maintenance</button>
        <button type="button">Create Work Order</button>
        <button type="button">Notify Supervisor</button>
        <button className="ack-action" type="button">Acknowledge</button>
      </div>
    </section>
  );
}

function toTimelineTone(severity: string): "good" | "warning" | "critical" {
  const normalized = severity.toUpperCase();
  if (normalized.includes("CRITICAL") || normalized.includes("90") || normalized.includes("100")) {
    return "critical";
  }
  if (normalized.includes("HIGH") || normalized.includes("MEDIUM") || normalized.includes("70") || normalized.includes("80")) {
    return "warning";
  }

  return "good";
}

function TimelineTab({ assetId }: { assetId: string }) {
  const timelineQuery = useAssetTimeline(assetId);

  if (timelineQuery.isLoading) {
    return (
      <section className="drawer-section">
        <h3>Asset Timeline</h3>
        <p className="prediction-empty">Loading telemetry events, alerts, and incidents...</p>
      </section>
    );
  }

  if (timelineQuery.isError || !timelineQuery.data) {
    return (
      <section className="drawer-section">
        <h3>Asset Timeline</h3>
        <p className="prediction-empty">Timeline unavailable for this asset.</p>
      </section>
    );
  }

  const entries = timelineQuery.data.timeline;

  return (
    <section className="drawer-section">
      <h3>Asset Timeline</h3>
      <ol className="timeline-list">
        {entries.map((event) => (
          <li className={toTimelineTone(event.severity)} key={`${event.entryType}-${event.timestamp}-${event.message}`}>
            <b>{event.entryType.replace(/_/g, " ")}</b>
            <span>{event.message}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

function PredictionExplanationPanel({ assetId }: { assetId: string }) {
  const historyQuery = useAssetHistory(assetId);

  if (historyQuery.isLoading) {
    return (
      <section className="drawer-section">
        <h3>Prediction Explanation</h3>
        <p className="prediction-empty">Analyzing historical telemetry drivers...</p>
      </section>
    );
  }

  if (historyQuery.isError || !historyQuery.data) {
    return (
      <section className="drawer-section">
        <h3>Prediction Explanation</h3>
        <p className="prediction-empty">No prediction explanation available.</p>
      </section>
    );
  }

  const explanation = historyQuery.data.predictionExplanation;
  const telemetryKeys = Object.keys(explanation.supportingTelemetryValues);

  return (
    <section className="drawer-section">
      <h3>Prediction Explanation</h3>
      <article className="prediction-panel">
        <div className="prediction-drivers">
          <span>Top Drivers</span>
          <ul>
            {explanation.topPredictionDrivers.map((driver) => (
              <li key={driver}>{driver}</li>
            ))}
          </ul>
        </div>
        <div className="prediction-support-grid">
          {telemetryKeys.map((key) => (
            <div key={key}>
              <span>{key}</span>
              <strong>{explanation.supportingTelemetryValues[key]}</strong>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}

function OperationalPrediction({ assetId }: { assetId: string }) {
  const predictionQuery = usePrediction(assetId);

  if (predictionQuery.isLoading) {
    return (
      <section className="drawer-section">
        <h3>Operational Prediction</h3>
        <p className="prediction-empty">Evaluating telemetry trends...</p>
      </section>
    );
  }

  if (predictionQuery.isError || !predictionQuery.data) {
    return (
      <section className="drawer-section">
        <h3>Operational Prediction</h3>
        <p className="prediction-empty">No active prediction for this asset.</p>
      </section>
    );
  }

  const prediction = predictionQuery.data;
  return (
    <section className="drawer-section">
      <h3>Operational Prediction</h3>
      <article className="prediction-panel">
        <div className="prediction-row"><span>Predicted Event</span><strong>{prediction.eventType.replace(/_/g, " ")}</strong></div>
        <div className="prediction-row"><span>Confidence</span><strong>{Math.round(prediction.confidence * 100)}%</strong></div>
        <div className="prediction-row"><span>Time To Event</span><strong>{prediction.timeToEventMinutes} min</strong></div>
        <div className="prediction-row"><span>Recommended Action</span><strong>{prediction.recommendedAction}</strong></div>
      </article>
    </section>
  );
}

function MlPredictionPanel({ assetId }: { assetId: string }) {
  const predictionQuery = useMlPrediction(assetId);

  if (predictionQuery.isLoading) {
    return (
      <section className="drawer-section">
        <h3>Machine Learning Prediction</h3>
        <p className="prediction-empty">Loading ML model output...</p>
      </section>
    );
  }

  if (predictionQuery.isError || !predictionQuery.data) {
    return (
      <section className="drawer-section">
        <h3>Machine Learning Prediction</h3>
        <p className="prediction-empty">No ML prediction available for this asset.</p>
      </section>
    );
  }

  const prediction = predictionQuery.data;
  return (
    <section className="drawer-section">
      <h3>Machine Learning Prediction</h3>
      <article className="ml-prediction-panel">
        <div className="prediction-row"><span>Predicted Event</span><strong>{prediction.predictedEvent.replace(/_/g, " ")}</strong></div>
        <div className="prediction-row"><span>Probability</span><strong>{Math.round(prediction.probability * 100)}%</strong></div>
        <div className="prediction-row"><span>Confidence</span><strong>{prediction.confidence}%</strong></div>
        <div className="prediction-row"><span>Model</span><strong>{prediction.modelVersion}</strong></div>
      </article>
    </section>
  );
}

export function AssetDrawer({ assetOverview, isLoading, onClose }: AssetDrawerProps) {
  const isOpen = Boolean(assetOverview) || isLoading;
  const measurements = assetOverview?.telemetry.measurements ?? {};
  const tone = assetOverview ? healthTone(assetOverview.health.riskLevel) : "normal";
  const isCritical = assetOverview?.health.riskLevel === "CRITICAL";
  const [activeTab, setActiveTab] = useState<"overview" | "timeline">("overview");

  useEffect(() => {
    setActiveTab("overview");
  }, [assetOverview?.asset.id]);

  return (
    <aside className={`asset-drawer ${isOpen ? "open" : ""}`} aria-label="Asset details">
      <div className="drawer-nav">
        <button type="button" onClick={onClose}><ArrowLeft size={17} />Back to Map</button>
        <button className="close-button" type="button" onClick={onClose} aria-label="Close asset drawer"><X size={18} /></button>
      </div>

      {isLoading ? (
        <div className="drawer-loading">Loading telemetry...</div>
      ) : assetOverview ? (
        <>
          <header className="asset-identity">
            <div className={`asset-icon-ring ${tone}`}><Truck size={24} /></div>
            <div>
              <h2>{assetOverview.asset.id}</h2>
              <span>{formatAssetType(assetOverview.asset.assetType)} - {assetOverview.asset.manufacturer} {assetOverview.asset.model}</span>
            </div>
            <b className={`status-badge ${tone}`}>{assetOverview.health.riskLevel}</b>
          </header>

          <div className="detail-grid">
            <DetailCell label="Engine" value={measurementText(measurements, "engine", "Running")} />
            <DetailCell label="Operator" value={measurementText(measurements, "operator", "M. Johnson")} />
            <DetailCell label="GPS" value={measurementText(measurements, "gps", "23.45S, 134.21E")} />
            <DetailCell label="Task" value={measurementText(measurements, "task", "Hauling/Crusher")} />
            <DetailCell label="Speed" value={`${measurementNumber(measurements, "speedKph", 0)} km/h`} />
            <DetailCell label="Hours" value={`${measurementNumber(measurements, "engineHours", 6240.2).toLocaleString()}h`} />
          </div>

          <div className="drawer-tabs" role="tablist" aria-label="Asset details tabs">
            <button className={activeTab === "overview" ? "active" : ""} type="button" onClick={() => setActiveTab("overview")}>Overview</button>
            <button className={activeTab === "timeline" ? "active" : ""} type="button" onClick={() => setActiveTab("timeline")}>Timeline</button>
          </div>

          {activeTab === "overview" ? (
            <>
              <HealthOverview assetOverview={assetOverview} />
              <TireMonitor assetOverview={assetOverview} />
              <RiskInsight assetOverview={assetOverview} />
              <OperationalPrediction assetId={assetOverview.asset.id} />
              <MlPredictionPanel assetId={assetOverview.asset.id} />
              <PredictionExplanationPanel assetId={assetOverview.asset.id} />
              <RecommendedActions assetOverview={assetOverview} isCritical={isCritical} />
            </>
          ) : (
            <TimelineTab assetId={assetOverview.asset.id} />
          )}
        </>
      ) : null}
    </aside>
  );
}
