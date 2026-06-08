from app.storage.analytics_service import analytics_service


class AnalyticsTool:
    def get_fleet_analytics(self) -> dict:
        return analytics_service.get_fleet_analytics().model_dump()
