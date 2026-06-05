from fastapi import APIRouter

from app.api.alerts import router as alerts_router
from app.api.assets import router as assets_router
from app.api.health import router as health_router

api_router = APIRouter()

api_router.include_router(assets_router)
api_router.include_router(health_router)
api_router.include_router(alerts_router)
