from fastapi import APIRouter, HTTPException

from app.prediction.ml.prediction_service import MlPrediction, PredictionService
from app.storage.repositories.mock_asset_repository import mock_asset_repository

router = APIRouter(prefix="/ml/predictions", tags=["ml-predictions"])
prediction_service = PredictionService()


@router.get("", response_model=list[MlPrediction])
def list_ml_predictions() -> list[MlPrediction]:
    assets = mock_asset_repository.list_assets()
    return prediction_service.predict_assets(assets)


@router.get("/{asset_id}", response_model=MlPrediction)
def get_ml_prediction(asset_id: str) -> MlPrediction:
    asset = mock_asset_repository.get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    prediction = prediction_service.predict_asset(asset)
    if prediction is None:
        raise HTTPException(status_code=404, detail="ML prediction not available for asset")

    return prediction
