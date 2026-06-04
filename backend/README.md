# Backend

FastAPI service for Equipment Guardian.

The backend owns API endpoints, persistence, asset-domain models, and pluggable prediction-engine boundaries. Core modules should model assets generically, with haul trucks represented as one asset type rather than the platform default.

## Stack

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

