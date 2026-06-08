from pathlib import Path

import xgboost as xgb

MODEL_VERSION = "tire-risk-v1"
MODEL_FILENAME = f"{MODEL_VERSION}.json"
MODEL_PATH = Path(__file__).resolve().parents[3] / "ml" / "haul_truck" / "models" / MODEL_FILENAME


class ModelLoader:
    def __init__(self, model_path: Path | None = None) -> None:
        self._model_path = model_path or MODEL_PATH

    def model_exists(self) -> bool:
        return self._model_path.exists()

    def load_active_model(self) -> xgb.Booster:
        if not self.model_exists():
            from app.prediction.ml.training_service import TrainingService

            TrainingService().ensure_model()

        if not self.model_exists():
            raise FileNotFoundError(f"ML model artifact not found: {self._model_path}")

        booster = xgb.Booster()
        booster.load_model(str(self._model_path))
        return booster

    @property
    def model_version(self) -> str:
        return MODEL_VERSION
