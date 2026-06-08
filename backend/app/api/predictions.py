from fastapi import APIRouter, HTTPException

from app.prediction.engine import prediction_engine
from app.prediction.models import Prediction
from app.storage.repositories.mock_asset_repository import mock_asset_repository

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=list[Prediction])
def list_predictions() -> list[Prediction]:
    assets = mock_asset_repository.list_assets()
    return prediction_engine.predict_assets(assets)


@router.get("/{asset_id}", response_model=Prediction)
def get_prediction(asset_id: str) -> Prediction:
    asset = mock_asset_repository.get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    prediction = prediction_engine.predict_asset(asset)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not available for asset")

    return prediction
