from app.storage.timeline_service import timeline_service


class TimelineTool:
    def get_asset_timeline(self, asset_id: str) -> dict | None:
        timeline = timeline_service.get_asset_timeline(asset_id)
        if timeline is None:
            return None
        return timeline.model_dump()

    def get_asset_history(self, asset_id: str) -> dict | None:
        history = timeline_service.get_asset_history(asset_id)
        if history is None:
            return None
        return history.model_dump()
