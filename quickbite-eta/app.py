"""
QuickBite ETA - FastAPI Serving
POST /predict with order details -> returns ETA in minutes
"""
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="QuickBite ETA")
model = joblib.load("eta_model.pkl")


class Order(BaseModel):
    distance_km: float
    prep_time_min: float
    rider_available: int
    is_raining: int


@app.get("/")
def health():
    return {"status": "QuickBite ETA is live 🛵"}


@app.post("/predict")
def predict(order: Order):
    X = pd.DataFrame([order.model_dump()])
    eta = round(float(model.predict(X)[0]), 1)
    return {"eta_minutes": eta, "message": f"Your food arrives in {eta} min 🍔"}
