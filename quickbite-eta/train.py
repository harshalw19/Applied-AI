"""
QuickBite ETA - Model Training
Trains a RandomForest on synthetic food-delivery data
and saves it as eta_model.pkl
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "distance_km": np.random.uniform(0.5, 12, n),
    "prep_time_min": np.random.uniform(5, 30, n),
    "rider_available": np.random.randint(0, 2, n),
    "is_raining": np.random.randint(0, 2, n),
})

# ETA = base + distance*3 + prep + rain penalty + rider penalty + noise
df["eta_min"] = (
    8
    + df.distance_km * 3
    + df.prep_time_min * 0.7
    + df.is_raining * 9
    + (1 - df.rider_available) * 6
    + np.random.normal(0, 2, n)
)

X, y = df.drop(columns=["eta_min"]), df["eta_min"]
model = RandomForestRegressor(n_estimators=60, random_state=42).fit(X, y)
joblib.dump(model, "eta_model.pkl")
print("Model saved: eta_model.pkl ✅")
