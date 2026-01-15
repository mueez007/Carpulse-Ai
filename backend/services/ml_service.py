from pathlib import Path
from typing import Optional

import joblib
import pandas as pd


# Resolve backend root: .../backend/ from this file
BACKEND_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BACKEND_DIR / "ml" / "service_cost_model.pkl"


class MLService:
    def __init__(self):
        self.model = None
        print(f"[ML] ml_service loaded from: {__file__}")
        print(f"[ML] Looking for model at: {MODEL_PATH}")
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"[ML] Loaded cost model from {MODEL_PATH}")
            except Exception as e:
                print(f"[ML] Error loading model from {MODEL_PATH}: {e}")
        else:
            print(f"[ML] Model file not found at {MODEL_PATH}. Train it first.")

    def is_ready(self) -> bool:
        return self.model is not None

    def estimate_cost(
        self,
        vehicle_model: str,
        service_type: str,
        mileage: int,
        mechanic_name: Optional[str] = None,
    ):
        """
        Run cost prediction using the trained pipeline.

        Features used (must match training script):
        - vehicle_model (str)
        - service_type (str)
        - mileage (int)
        - mechanic_name (str, can be empty)
        """
        if not self.model:
            raise RuntimeError("ML model not loaded")

        # Build a DataFrame with the SAME column names as training
        df = pd.DataFrame(
            [
                {
                    "vehicle_model": vehicle_model,
                    "service_type": service_type,
                    "mileage": mileage,
                    "mechanic_name": mechanic_name or "",
                }
            ]
        )

        print("[ML] Predict input DataFrame:")
        print(df)
        print("[ML] dtypes:", df.dtypes)

        pred = float(self.model.predict(df)[0])

        low = round(pred * 0.9)
        high = round(pred * 1.1)

        return {
            "predicted_cost": round(pred),
            "range_low": low,
            "range_high": high,
        }


# Single shared instance
ml_service = MLService()
