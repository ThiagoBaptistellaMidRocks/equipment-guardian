# Equipment Guardian

Equipment Guardian is an AI-powered mining equipment intelligence platform.

The platform is organized around mining assets rather than a single equipment class. Haul truck tire overheating prediction is the first implementation target, with the repository shaped so excavators, drills, dozers, graders, and future intelligence domains can be added without changing core platform assumptions.

## Repository Layout

- `frontend/` - React, TypeScript, Vite application shell.
- `backend/` - FastAPI service, domain modules, persistence, and prediction-engine interfaces.
- `shared/` - Shared contracts and schemas used across services.
- `data/` - Local development data staging for assets, routes, weather, and events.
- `ml/` - Asset and maintenance-specific machine learning workspaces.
- `docs/` - Architecture, roadmap, data-contract, and AI-strategy documentation.
- `infra/` - Docker and infrastructure configuration.
- `scripts/` - Developer automation and maintenance scripts.

## Principles

- Build around assets, not trucks.
- Keep asset types extensible.
- Keep prediction engines pluggable.
- Isolate AI agents by domain.
- Treat shared contracts as the source of truth.

## Getting Started

This scaffold does not implement business logic yet.

```bash
docker compose up --build
```
