from fastapi import APIRouter

from app.history.analytics_service import FleetAnalytics, analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/fleet", response_model=FleetAnalytics)
def get_fleet_analytics() -> FleetAnalytics:
    return analytics_service.get_fleet_analytics()
