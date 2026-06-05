import { Maximize2 } from "lucide-react";
import { useFleetAnalytics } from "../hooks/useAssets";

function formatTrend(values: number[]): string {
  if (values.length < 2) {
    return "Stable";
  }

  const delta = values[values.length - 1] - values[0];
  const direction = delta >= 0 ? "+" : "";
  return `${direction}${delta.toFixed(1)} over window`;
}

export function OperationsKpis() {
  const analyticsQuery = useFleetAnalytics();

  if (analyticsQuery.isLoading || !analyticsQuery.data) {
    return (
      <section className="kpi-panel">
        <div className="panel-title">
          <h2>Operations KPIs</h2>
          <Maximize2 size={16} />
        </div>
        <div className="kpi-grid">
          <article>
            <span>Failure Trends</span>
            <strong>Loading</strong>
            <small>Gathering historical intelligence</small>
          </article>
        </div>
      </section>
    );
  }

  const analytics = analyticsQuery.data;
  const failureValues = analytics.failureTrends.map((point) => point.value);
  const healthValues = analytics.fleetHealthTrends.map((point) => point.value);

  return (
    <section className="kpi-panel">
      <div className="panel-title">
        <h2>Operations KPIs</h2>
        <Maximize2 size={16} />
      </div>
      <div className="kpi-grid">
        <article>
          <span>Failure Trends</span>
          <strong className="orange">{failureValues[failureValues.length - 1] ?? 0}</strong>
          <small>{formatTrend(failureValues)}</small>
        </article>
        <article>
          <span>Fleet Health Trends</span>
          <strong>{healthValues[healthValues.length - 1]?.toFixed(1) ?? "0.0"}</strong>
          <small>{formatTrend(healthValues)}</small>
        </article>
        <article>
          <span>Predicted Failures</span>
          <strong className="orange">{analytics.predictedFailures}</strong>
          <small>Next operational window</small>
        </article>
        <article>
          <span>Downtime Avoided</span>
          <strong className="good">{analytics.downtimeAvoided.toFixed(1)} hrs</strong>
          <small>Projected from proactive interventions</small>
        </article>
      </div>
    </section>
  );
}
