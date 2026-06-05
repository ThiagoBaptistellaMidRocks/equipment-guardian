import { Activity, AlertTriangle, CircleAlert, Gauge, Timer } from "lucide-react";
import type { AssetOverview } from "../types/assets";

export function FleetSummary({ assets }: { assets: AssetOverview[] }) {
  const critical = assets.filter(({ health }) => health.riskLevel === "CRITICAL").length;
  const atRisk = assets.filter(({ health }) => health.riskLevel === "HIGH" || health.riskLevel === "CRITICAL").length;
  const averageFleetHealth = assets.length
    ? Math.round(assets.reduce((total, { health }) => total + health.healthScore, 0) / assets.length)
    : 0;

  return (
    <section className="fleet-summary">
      <div className="panel-title">
        <h2>Fleet Summary</h2>
        <span>Live</span>
      </div>
      <dl className="summary-list">
        <div><dt><Gauge size={15} />Average Fleet Health</dt><dd>{averageFleetHealth}</dd></div>
        <div><dt><Activity size={15} />Total Assets</dt><dd className="good">{assets.length}</dd></div>
        <div><dt><AlertTriangle size={15} />Assets At Risk</dt><dd className="warning">{atRisk}</dd></div>
        <div><dt><CircleAlert size={15} />Critical Assets</dt><dd className="critical">{critical}</dd></div>
        <div><dt><Timer size={15} />Watchlist</dt><dd className="warning">{atRisk}</dd></div>
      </dl>
      <div className="cycle-row">
        <span>Haul Cycle Time</span>
        <strong>28.2 min avg</strong>
      </div>
      <div className="cycle-bars" aria-hidden="true">
        {[0.66, 0.8, 0.56, 0.74, 0.5].map((height, index) => (
          <span key={index} style={{ height: `${height * 38}px` }} />
        ))}
      </div>
    </section>
  );
}
