from fastapi import APIRouter

from app.api.analytics import router as analytics_router
from app.api.alerts import router as alerts_router
from app.api.copilot import router as copilot_router
from app.api.assets import router as assets_router
from app.api.health import router as health_router
from app.api.ml_predictions import router as ml_predictions_router
from app.api.predictions import router as predictions_router

api_router = APIRouter()

api_router.include_router(assets_router)
api_router.include_router(health_router)
api_router.include_router(alerts_router)
api_router.include_router(predictions_router)
api_router.include_router(ml_predictions_router)
api_router.include_router(analytics_router)
api_router.include_router(copilot_router)
