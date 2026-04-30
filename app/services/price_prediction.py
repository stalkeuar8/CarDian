import joblib
import pandas as pd
import numpy as np

from app.schemas.prediction_schemas import BasePredictor

class PredictService:

    def __init__(self, models_path: str = "ml/models/v2_stable_xg_boost"):
        self.router = joblib.load(f"{models_path}/router_model.pkl")
        self.models = {
            0: joblib.load(f"{models_path}/xg_cheap_model.pkl"),
            1: joblib.load(f"{models_path}/xg_medium_model.pkl"),
            2: joblib.load(f"{models_path}/xg_exp_model.pkl")
        }

    def predict(self, data_to_predict: BasePredictor) -> int | None:
        df_input = pd.DataFrame([data_to_predict.model_dump()])

        segment = self.router.predict(df_input)[0]

        log_price = self.models[segment].predict(df_input)[0]

        price = int(np.expm1(log_price))

        return price
    

predict_service = PredictService()
