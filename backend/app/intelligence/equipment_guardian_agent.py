from dataclasses import dataclass

from app.intelligence.tools.analytics_tool import AnalyticsTool
from app.intelligence.tools.asset_tool import AssetTool
from app.intelligence.tools.health_tool import HealthTool
from app.intelligence.tools.prediction_tool import PredictionTool
from app.intelligence.tools.timeline_tool import TimelineTool

SYSTEM_PROMPT = """
You are the Equipment Guardian mining operations intelligence assistant.

You must:
- Explain asset health.
- Explain predictions.
- Explain incidents.
- Recommend actions.
- Use platform data only.
- Never invent telemetry.
""".strip()


@dataclass
class CopilotContext:
    message: str
    focus_assets: list[str]
    assets: dict[str, dict]
    health: dict[str, dict]
    predictions: dict[str, dict]
    timelines: dict[str, dict]
    histories: dict[str, dict]
    fleet_analytics: dict


class ContextBuilder:
    def __init__(
        self,
        asset_tool: AssetTool,
        health_tool: HealthTool,
        prediction_tool: PredictionTool,
        timeline_tool: TimelineTool,
        analytics_tool: AnalyticsTool,
    ) -> None:
        self._asset_tool = asset_tool
        self._health_tool = health_tool
        self._prediction_tool = prediction_tool
        self._timeline_tool = timeline_tool
        self._analytics_tool = analytics_tool

    def build(self, message: str) -> CopilotContext:
        mentioned_assets = self._asset_tool.extract_asset_ids(message)
        fleet_analytics = self._analytics_tool.get_fleet_analytics()

        if mentioned_assets:
            focus_assets = mentioned_assets
        else:
            focus_assets = fleet_analytics.get("assetsWithHighestRisk", [])[:1]
            if not focus_assets:
                first_asset = self._asset_tool.list_assets()[:1]
                focus_assets = [asset.asset.id for asset in first_asset]

        assets: dict[str, dict] = {}
        health: dict[str, dict] = {}
        predictions: dict[str, dict] = {}
        timelines: dict[str, dict] = {}
        histories: dict[str, dict] = {}

        for asset_id in focus_assets:
            overview = self._asset_tool.get_asset(asset_id)
            if overview is None:
                continue
            assets[asset_id] = overview.model_dump()
            health[asset_id] = self._health_tool.get_asset_health(asset_id) or {}
            predictions[asset_id] = self._prediction_tool.get_asset_predictions(asset_id)
            timelines[asset_id] = self._timeline_tool.get_asset_timeline(asset_id) or {}
            histories[asset_id] = self._timeline_tool.get_asset_history(asset_id) or {}

        return CopilotContext(
            message=message,
            focus_assets=focus_assets,
            assets=assets,
            health=health,
            predictions=predictions,
            timelines=timelines,
            histories=histories,
            fleet_analytics=fleet_analytics,
        )


class EquipmentGuardianAgent:
    def __init__(self) -> None:
        self._asset_tool = AssetTool()
        self._health_tool = HealthTool()
        self._prediction_tool = PredictionTool()
        self._timeline_tool = TimelineTool()
        self._analytics_tool = AnalyticsTool()
        self._context_builder = ContextBuilder(
            asset_tool=self._asset_tool,
            health_tool=self._health_tool,
            prediction_tool=self._prediction_tool,
            timeline_tool=self._timeline_tool,
            analytics_tool=self._analytics_tool,
        )

    def chat(self, message: str) -> str:
        context = self._context_builder.build(message)
        lowered = message.lower()

        if any(keyword in lowered for keyword in ["why", "risk", "at risk", "health"]):
            return self._explain_risk(context)
        if any(keyword in lowered for keyword in ["predict", "prediction", "ml", "probability"]):
            return self._explain_predictions(context)
        if any(keyword in lowered for keyword in ["incident", "timeline", "event", "history"]):
            return self._explain_timeline(context)
        if any(keyword in lowered for keyword in ["fleet", "analytics", "trend", "downtime"]):
            return self._explain_fleet(context)

        return self._default_response(context)

    def _explain_risk(self, context: CopilotContext) -> str:
        lines: list[str] = []
        for asset_id in context.focus_assets:
            if asset_id not in context.assets:
                continue

            health = context.health.get(asset_id, {})
            alerts = health.get("activeAlerts", [])
            history = context.histories.get(asset_id, {})
            explanation = history.get("predictionExplanation", {})

            lines.append(
                f"{asset_id} is {health.get('riskLevel', 'UNKNOWN')} risk with health score {health.get('healthScore', 'N/A')}."
            )

            if alerts:
                top_alert = alerts[0]
                lines.append(
                    f"Top active alert: {top_alert.get('message', 'N/A')} (severity {top_alert.get('severity', 'N/A')})."
                )

            drivers = explanation.get("topPredictionDrivers", [])
            if drivers:
                lines.append(f"Primary drivers: {', '.join(drivers[:3])}.")

            support = explanation.get("supportingTelemetryValues", {})
            if support:
                support_pairs = [f"{key}={value}" for key, value in support.items()]
                lines.append(f"Supporting telemetry: {', '.join(support_pairs)}.")

            recommendation = self._recommended_action(context, asset_id)
            if recommendation:
                lines.append(f"Recommended action: {recommendation}.")

        return "\n".join(lines) if lines else "I could not find that asset in platform data."

    def _explain_predictions(self, context: CopilotContext) -> str:
        lines: list[str] = []
        for asset_id in context.focus_assets:
            prediction = context.predictions.get(asset_id, {})
            rule = prediction.get("rulePrediction")
            ml = prediction.get("mlPrediction")

            if rule is not None:
                lines.append(
                    (
                        f"{asset_id} rule prediction: {rule.get('eventType')} "
                        f"with confidence {round(float(rule.get('confidence', 0)) * 100)}% "
                        f"in about {rule.get('timeToEventMinutes')} minutes."
                    )
                )
                lines.append(f"Rule recommendation: {rule.get('recommendedAction')}.")

            if ml is not None:
                lines.append(
                    (
                        f"{asset_id} ML prediction: {ml.get('predictedEvent')} with probability "
                        f"{round(float(ml.get('probability', 0)) * 100)}% and confidence {ml.get('confidence')}% "
                        f"(model {ml.get('modelVersion')})."
                    )
                )

            if rule is None and ml is None:
                lines.append(f"No prediction is currently available for {asset_id}.")

        return "\n".join(lines) if lines else "No prediction context is available."

    def _explain_timeline(self, context: CopilotContext) -> str:
        lines: list[str] = []
        for asset_id in context.focus_assets:
            timeline = context.timelines.get(asset_id, {}).get("timeline", [])
            if not timeline:
                lines.append(f"No timeline events found for {asset_id}.")
                continue

            lines.append(f"Recent timeline for {asset_id}:")
            for event in timeline[:5]:
                lines.append(
                    f"- {event.get('entryType')}: {event.get('message')} (severity {event.get('severity')})"
                )

            recommendation = self._recommended_action(context, asset_id)
            if recommendation:
                lines.append(f"Recommended action: {recommendation}.")

        return "\n".join(lines)

    def _explain_fleet(self, context: CopilotContext) -> str:
        analytics = context.fleet_analytics
        assets_with_risk = analytics.get("assetsWithHighestRisk", [])

        return (
            "Fleet analytics snapshot:\n"
            f"- Predicted failures: {analytics.get('predictedFailures')}\n"
            f"- Downtime avoided: {analytics.get('downtimeAvoided')} hours\n"
            f"- Average ML confidence: {analytics.get('averagePredictionConfidence')}%\n"
            f"- Highest risk assets: {', '.join(assets_with_risk) if assets_with_risk else 'None'}"
        )

    def _default_response(self, context: CopilotContext) -> str:
        if context.focus_assets:
            primary = context.focus_assets[0]
            return (
                f"I can help with health, predictions, incidents, timelines, and fleet analytics. "
                f"For example: ask why {primary} is at risk, ask for its latest predictions, "
                "or ask for fleet trends and downtime avoided."
            )

        return "I can help with asset health, predictions, incidents, and fleet analytics using Equipment Guardian data."

    def _recommended_action(self, context: CopilotContext, asset_id: str) -> str | None:
        prediction = context.predictions.get(asset_id, {})
        rule = prediction.get("rulePrediction")
        if rule is not None and rule.get("recommendedAction"):
            return str(rule.get("recommendedAction"))

        health = context.health.get(asset_id, {})
        alerts = health.get("activeAlerts", [])
        if alerts:
            top_alert = alerts[0]
            return f"Investigate alert {top_alert.get('code')} and stabilize {top_alert.get('metric')}"

        return None


equipment_guardian_agent = EquipmentGuardianAgent()
