from app.prediction.ml.prediction_service import PredictionService
from app.prediction.engine import prediction_engine
from app.storage.repositories.mock_asset_repository import mock_asset_repository


class PredictionTool:
    def __init__(self, ml_prediction_service: PredictionService | None = None) -> None:
        self._ml_prediction_service = ml_prediction_service or PredictionService()

    def get_asset_predictions(self, asset_id: str) -> dict:
        asset = mock_asset_repository.get_asset(asset_id)
        if asset is None:
            return {"rulePrediction": None, "mlPrediction": None}

        rule_prediction = prediction_engine.predict_asset(asset)
        ml_prediction = self._ml_prediction_service.predict_asset(asset)

        return {
            "rulePrediction": rule_prediction.model_dump() if rule_prediction is not None else None,
            "mlPrediction": ml_prediction.model_dump() if ml_prediction is not None else None,
        }
