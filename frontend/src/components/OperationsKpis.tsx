import { Maximize2 } from "lucide-react";

export function OperationsKpis() {
  return (
    <section className="kpi-panel">
      <div className="panel-title">
        <h2>Operations KPIs</h2>
        <Maximize2 size={16} />
      </div>
      <div className="kpi-grid">
        <article>
          <span>Fleet Availability</span>
          <strong className="orange">87.3%</strong>
          <small>+2.1% vs yesterday</small>
        </article>
        <article>
          <span>Downtime Avoided</span>
          <strong>4.2 hrs</strong>
          <small>This shift</small>
        </article>
        <article>
          <span>Failures Prevented</span>
          <strong className="orange">2</strong>
          <small>Maintenance flags</small>
        </article>
        <article>
          <span>Production Impact</span>
          <strong className="good">+$128K</strong>
          <small>Savings today</small>
        </article>
      </div>
    </section>
  );
}
