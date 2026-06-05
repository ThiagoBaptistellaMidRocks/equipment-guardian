from app.domain.assets import AssetOverview
from app.prediction.models import Prediction, PredictionInput
from app.prediction.predictor import TrendPredictor


class PredictionEngine:
    def __init__(self, predictor: TrendPredictor | None = None) -> None:
        self._predictor = predictor or TrendPredictor()

    def predict_asset(self, asset_overview: AssetOverview) -> Prediction | None:
        prediction_input = PredictionInput(
            assetId=asset_overview.asset.id,
            assetType=asset_overview.asset.assetType,
            currentTelemetry=asset_overview.telemetry.measurements,
            historicalTelemetry=self._historical_samples(asset_overview.telemetry.measurements),
        )
        return self._predictor.predict(prediction_input)

    def predict_assets(self, asset_overviews: list[AssetOverview]) -> list[Prediction]:
        predictions: list[Prediction] = []

        for asset_overview in asset_overviews:
            prediction = self.predict_asset(asset_overview)
            if prediction is not None:
                predictions.append(prediction)

        return predictions

    def _historical_samples(self, measurements: dict[str, float | str | bool | None]) -> list[dict[str, float | str | bool | None]]:
        factors = [0.82, 0.88, 0.93, 0.97, 1.0]
        samples: list[dict[str, float | str | bool | None]] = []

        for factor in factors:
            sample: dict[str, float | str | bool | None] = {}
            for key, value in measurements.items():
                if isinstance(value, (int, float)):
                    if "Psi" in key:
                        sample[key] = round(float(value) + ((1 - factor) * 4), 2)
                    else:
                        sample[key] = round(float(value) * factor, 2)
                else:
                    sample[key] = value

            samples.append(sample)

        return samples


prediction_engine = PredictionEngine()
