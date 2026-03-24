from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"
MODELS_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)

rng = np.random.default_rng(42)
n = 20000

crops = np.array(["tomato", "capsicum", "potato", "pea", "apple"])
land_type = np.array(["owned", "rented"])

df = pd.DataFrame(
    {
        "crop_name": rng.choice(crops, n),
        "land_type": rng.choice(land_type, n, p=[0.55, 0.45]),
        "land_area_acre": rng.uniform(0.25, 8.0, n),
        "duration_months": rng.integers(3, 9, n),
        "labor_count": rng.integers(1, 12, n),
        "labor_daily_wage_inr": rng.uniform(450, 1100, n),
        "self_work_hours_per_day": rng.uniform(0, 6, n),
        "water_cycles": rng.integers(2, 18, n),
        "water_cost_per_cycle_inr": rng.uniform(600, 5000, n),
        "seed_cost_inr": rng.uniform(2000, 30000, n),
        "fertilizer_cost_inr": rng.uniform(5000, 50000, n),
        "pesticide_cost_inr": rng.uniform(1500, 35000, n),
        "insecticide_cost_inr": rng.uniform(1000, 25000, n),
        "spray_cost_inr": rng.uniform(1000, 22000, n),
        "tractor_cost_inr": rng.uniform(0, 30000, n),
        "transport_to_market_inr": rng.uniform(1000, 18000, n),
        "misc_cost_inr": rng.uniform(1000, 25000, n),
    }
)

df["land_rent_inr"] = np.where(
    df["land_type"] == "rented",
    df["land_area_acre"] * rng.uniform(18000, 55000, n),
    0,
)

altitude_factor = rng.uniform(0.95, 1.15, n)  # Himachal-like terrain effect
base_total = (
    df["land_rent_inr"]
    + df["labor_count"] * df["labor_daily_wage_inr"] * df["duration_months"] * 26
    + df["self_work_hours_per_day"] * 70 * df["duration_months"] * 26
    + df["water_cycles"] * df["water_cost_per_cycle_inr"]
    + df["seed_cost_inr"]
    + df["fertilizer_cost_inr"]
    + df["pesticide_cost_inr"]
    + df["insecticide_cost_inr"]
    + df["spray_cost_inr"]
    + df["tractor_cost_inr"]
    + df["transport_to_market_inr"]
    + df["misc_cost_inr"]
)
df["total_cost_inr"] = base_total * altitude_factor + rng.normal(0, 9000, n)
df["total_cost_inr"] = df["total_cost_inr"].clip(lower=25000)

csv_path = DATA_DIR / "himachal_crop_cost_20k.csv"
df.to_csv(csv_path, index=False)

target = "total_cost_inr"
feature_cols = [c for c in df.columns if c != target]
X = df[feature_cols]
y = df[target]

cat_cols = ["crop_name", "land_type"]
num_cols = [c for c in feature_cols if c not in cat_cols]

encoder = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ("num", "passthrough", num_cols),
    ]
)
X_encoded = encoder.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
score = model.score(X_test, y_test)

joblib.dump(model, MODELS_DIR / "cost_estimator.joblib")
joblib.dump(encoder, MODELS_DIR / "cost_feature_encoder.joblib")
print(f"Saved cost model. R2 score: {score:.4f}")
print(f"Dataset saved to: {csv_path}")
