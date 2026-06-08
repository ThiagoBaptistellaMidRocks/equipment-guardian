# Data Flow

This document describes the runtime pipeline from telemetry ingestion to UI rendering.

## End-to-End Flow

```mermaid
flowchart LR
  telemetry[Telemetry + context input]
  storage_repo[storage/repositories/mock_asset_repository.py]
  health_engine[health/engine.py]
  prediction_rule[prediction/engine.py]
  prediction_ml[prediction/ml/prediction_service.py]
  storage_history[storage/telemetry_history.py]
  timeline_service[storage/timeline_service.py]
  analytics_service[storage/analytics_service.py]
  intelligence_agent[intelligence/equipment_guardian_agent.py]
  api[FastAPI routes]
  ui_map[UI: map and asset states]
  ui_drawer[UI: drawer health/predictions/timeline]
  ui_kpi[UI: fleet analytics KPIs]
  ui_copilot[UI: copilot conversation]

  telemetry --> storage_repo
  storage_repo --> health_engine
  storage_repo --> prediction_rule
  storage_repo --> prediction_ml
  storage_repo --> storage_history

  storage_history --> timeline_service
  storage_history --> analytics_service

  health_engine --> api
  prediction_rule --> api
  prediction_ml --> api
  timeline_service --> api
  analytics_service --> api

  health_engine --> intelligence_agent
  prediction_rule --> intelligence_agent
  prediction_ml --> intelligence_agent
  timeline_service --> intelligence_agent
  analytics_service --> intelligence_agent
  intelligence_agent --> api

  api --> ui_map
  api --> ui_drawer
  api --> ui_kpi
  api --> ui_copilot
```

## Processing Sequence

1. Telemetry and operational context are loaded via the storage repository layer.
2. Health rules compute risk level, health score, and active alerts.
3. Prediction engine computes rule-based event risk and recommended action.
4. ML inference computes probability and confidence from engineered features.
5. Historical telemetry is used to assemble timeline events and prediction explanation context.
6. Fleet analytics aggregates trends such as predicted failures and downtime avoided.
7. Copilot intelligence composes answers strictly from platform data.
8. API routes return composed responses to the React frontend.
9. UI renders map badges, drawer details, KPI panels, and copilot conversations.

## API Touchpoints

- `/api/assets` and `/api/assets/{id}`: asset details and current telemetry.
- `/api/health`: fleet health state.
- `/api/alerts`: active alert projections.
- `/api/predictions` and `/api/predictions/{id}`: rule predictions.
- `/api/ml/predictions` and `/api/ml/predictions/{id}`: ML predictions.
- `/api/assets/{id}/history`: prediction explanation context.
- `/api/assets/{id}/timeline`: timeline events.
- `/api/analytics/fleet`: fleet trends and operational impact metrics.
- `/api/copilot/chat`: operational intelligence assistant responses.
