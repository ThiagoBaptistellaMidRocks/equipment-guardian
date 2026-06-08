# Equipment Guardian Architecture

Equipment Guardian is an operational intelligence platform for mining assets.

It is organized into four backend domains:

- `prediction/`: health-adjacent prediction logic and ML pipeline.
- `storage/`: historical telemetry, timeline assembly, and repositories.
- `intelligence/`: Equipment Guardian Copilot orchestration and tools.
- `integrations/`: external connectors and adapter entry points.

## System Diagram

```mermaid
flowchart LR
	subgraph Data[Operational Data Sources]
		telemetry[Telemetry streams]
		weather[Weather context]
		events[Events and incidents]
		ops[Route and payload context]
	end

	subgraph API[FastAPI API Surface]
		assets_api[/assets]
		health_api[/health]
		alerts_api[/alerts]
		pred_api[/predictions]
		ml_api[/ml/predictions]
		analytics_api[/analytics/fleet]
		copilot_api[/copilot/chat]
	end

	subgraph Backend[Backend Application]
		subgraph Domain[Core Domain]
			assets_domain[domain/assets.py]
			health_engine[health/engine.py]
			alerts_service[alerts/service.py]
		end

		subgraph Prediction[Prediction Layer]
			rule_engine[prediction/engine.py]
			trend_predictor[prediction/predictor.py]
			ml_features[prediction/ml/feature_builder.py]
			ml_training[prediction/ml/training_service.py]
			ml_inference[prediction/ml/prediction_service.py]
			ml_loader[prediction/ml/model_loader.py]
		end

		subgraph Storage[Storage Layer]
			repo[storage/repositories/mock_asset_repository.py]
			telemetry_history[storage/telemetry_history.py]
			timeline_service[storage/timeline_service.py]
			analytics_service[storage/analytics_service.py]
			event_history[storage/event_history.py]
		end

		subgraph Intelligence[Intelligence Layer]
			copilot_agent[intelligence/equipment_guardian_agent.py]
			copilot_tools[intelligence/tools/*.py]
		end

		subgraph Integrations[Integrations Layer]
			adapters[integrations/]
		end
	end

	subgraph Frontend[React + TypeScript UI]
		map_ui[Operations Map]
		drawer_ui[Asset Drawer]
		kpi_ui[Operations KPIs]
		copilot_ui[Copilot Panel]
	end

	telemetry --> repo
	weather --> repo
	events --> repo
	ops --> repo

	repo --> assets_domain
	assets_domain --> health_engine
	assets_domain --> rule_engine
	assets_domain --> ml_inference
	repo --> telemetry_history
	telemetry_history --> timeline_service
	telemetry_history --> analytics_service
	event_history --> timeline_service
	ml_features --> ml_training
	ml_loader --> ml_inference

	health_engine --> health_api
	alerts_service --> alerts_api
	rule_engine --> pred_api
	ml_inference --> ml_api
	timeline_service --> assets_api
	analytics_service --> analytics_api

	health_engine --> copilot_tools
	rule_engine --> copilot_tools
	ml_inference --> copilot_tools
	timeline_service --> copilot_tools
	analytics_service --> copilot_tools
	copilot_tools --> copilot_agent
	copilot_agent --> copilot_api

	assets_api --> map_ui
	assets_api --> drawer_ui
	health_api --> drawer_ui
	pred_api --> drawer_ui
	ml_api --> drawer_ui
	analytics_api --> kpi_ui
	copilot_api --> copilot_ui
```

## Backend Structure

```text
backend/app/
	api/            # FastAPI routes
	domain/         # Shared domain models
	health/         # Health scoring and rules
	alerts/         # Alert projection logic
	prediction/     # Rule prediction + ML pipeline
	storage/        # Repositories + timeline + analytics history
	intelligence/   # Copilot agent and tools
	integrations/   # External connectors (adapter boundary)
	config/         # Runtime settings
	main.py         # FastAPI application entrypoint
```

