# Equipment Guardian

## Mission

Equipment Guardian is an AI-powered mining equipment intelligence platform.

The platform must support multiple asset types:

- Haul Trucks
- Excavators
- Drills
- Dozers
- Graders

The first implementation is Haul Truck tire overheating prediction.

Future implementations will include:

- Predictive maintenance
- Downtime prediction
- Reliability scoring
- Production optimization
- Safety intelligence

## Architecture Rules

- Backend = FastAPI
- Frontend = React + TypeScript + Vite
- Database = PostgreSQL
- Infrastructure = Docker

## Design Principles

- Build around Assets, not Trucks.
- Asset types must be extensible.
- Prediction engines must be pluggable.
- AI Agents must be isolated by domain.
- Shared contracts are the source of truth.

## Never Do

- Do not hardcode haul truck assumptions into core platform components.
- Do not create AI-specific code inside UI components.
- Do not couple adapters to prediction logic.