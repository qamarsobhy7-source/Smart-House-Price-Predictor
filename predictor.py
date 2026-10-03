"""
Smart House Price Predictor — v9 Adapter
Loads FINAL_MODEL_v9.pkl and provides original interface.
"""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "FINAL_MODEL_v9.pkl"
FEATURES_PATH = MODELS_DIR / "FINAL_FEATURES_v9.pkl"
CAT_FEATURES_PATH = MODELS_DIR / "FINAL_CAT_FEATURES_v9.pkl"


# ═══════════════════════════════════════════════════════
# LOAD ARTIFACTS
# ═══════════════════════════════════════════════════════
def load_artifacts():
    """Load model + metadata + mappings."""
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    cat_features = joblib.load(CAT_FEATURES_PATH)

    metadata = {
        "model_name": "CatBoost",
        "model_version": "v9",
        "r2_score": 0.7061,
        "mape": 40.52,
        "accuracy": "70.6%",
        "error": "40.52%",
        "n_features": len(features),
        "features": features,
        "cat_features": cat_features,
        "total_listings": 119916,
        "governorates": 6,
        "districts": 573,
        "compounds": 881,
    }

    # Categorical values for dropdowns
    try:
        df = pd.read_csv(BASE_DIR / "data" / "processed" / "FINAL_DATASET_v9.csv")
        categorical_values = {}
        for col in cat_features:
            categorical_values[col] = sorted(df[col].dropna().astype(str).unique().tolist())
    except Exception:
        categorical_values = {
            "property_type": ["Apartment", "Villa", "Townhouse", "Duplex",
                              "Penthouse", "Twin House", "iVilla",
                              "Hotel Apartment", "Chalet"],
            "governorate": ["Cairo", "Giza", "Matrouh", "Red Sea",
                            "Alexandria", "Suez"],
        }

    mappings = {
        "categorical_values": categorical_values,
        "num_features": [f for f in features if f not in cat_features],
        "cat_features": cat_features,
    }

    return model, metadata, mappings


def get_category_values(mappings):
    """Return categorical values for dropdowns."""
    return mappings["categorical_values"]


# ═══════════════════════════════════════════════════════
# VALIDATE INPUT
# ═══════════════════════════════════════════════════════
def validate_input(area, bedrooms, bathrooms, city, district, compound,
                   price=None):
    """Validate user input."""
    errors = []

    try:
        area_val = float(area)
        if not np.isfinite(area_val) or area_val <= 0:
            errors.append("Area must be a positive number.")
        elif area_val < 20 or area_val > 5000:
            errors.append("Area must be between 20 and 5000 sqm.")
    except (TypeError, ValueError):
        errors.append("Area is invalid.")

    try:
        bd = int(bedrooms)
        if bd < 0 or bd > 15:
            errors.append("Bedrooms must be between 0 and 15.")
    except (TypeError, ValueError):
        errors.append("Bedrooms value is invalid.")

    try:
        ba = int(bathrooms)
        if ba < 1 or ba > 15:
            errors.append("Bathrooms must be between 1 and 15.")
    except (TypeError, ValueError):
        errors.append("Bathrooms value is invalid.")

    required = {"City": city, "District": district}
    for label, value in required.items():
        if value is None or not str(value).strip():
            errors.append(f"{label} is required.")

    return errors


# ═══════════════════════════════════════════════════════
# BUILD FEATURES
# ═══════════════════════════════════════════════════════
def build_features(input_dict, features, cat_features):
    """Build feature vector for v9 model."""
    row = {}
    for f in features:
        if f in cat_features:
            row[f] = str(input_dict.get(f, "Unknown"))
        else:
            row[f] = float(input_dict.get(f, 0))

    return pd.DataFrame([row])[features]


# ═══════════════════════════════════════════════════════
# PREDICT
# ═══════════════════════════════════════════════════════
def predict_with_confidence(model, X, features, cat_features):
    """Predict price + confidence interval."""
    try:
        log_price = model.predict(X)[0]
        price = float(np.expm1(log_price))

        # Confidence ± MAPE
        mape = 0.4052
        low = price * (1 - mape)
        high = price * (1 + mape)

        return {
            "price": price,
            "price_low": low,
            "price_high": high,
            "confidence": 0.71,
            "log_price": float(log_price),
        }
    except Exception as e:
        return {"error": str(e), "price": 0}


# ═══════════════════════════════════════════════════════
# FORMAT PRICE
# ═══════════════════════════════════════════════════════
def format_price(price, lang="en"):
    """Format price with commas and currency."""
    if price >= 1_000_000:
        m = price / 1_000_000
        if lang == "ar":
            return f"{m:.2f} مليون جنيه"
        return f"EGP {m:.2f}M"
    elif price >= 1_000:
        k = price / 1_000
        if lang == "ar":
            return f"{k:.0f} ألف جنيه"
        return f"EGP {k:.0f}K"
    return f"EGP {price:,.0f}"


# ═══════════════════════════════════════════════════════
# ROI
# ═══════════════════════════════════════════════════════
def calculate_roi(price, years=5, growth_rate=0.08):
    """Calculate ROI over time."""
    future = price * ((1 + growth_rate) ** years)
    roi_pct = ((future - price) / price) * 100
    return {
        "current_price": price,
        "future_price": future,
        "roi_percent": roi_pct,
        "gain": future - price,
        "years": years,
    }


# ═══════════════════════════════════════════════════════
# SIMILAR PROPERTIES
# ═══════════════════════════════════════════════════════
def recommend_similar_properties(df, governorate, property_type, size,
                                  price, top_n=3):
    """Find similar properties."""
    try:
        filtered = df[
            (df["governorate"] == governorate) &
            (df["property_type"] == property_type) &
            (df["size"].between(size * 0.8, size * 1.2))
        ].copy()

        if len(filtered) == 0:
            filtered = df[df["governorate"] == governorate].head(top_n)

        filtered["price_diff"] = abs(filtered["price"] - price)
        result = filtered.nsmallest(top_n, "price_diff")

        return result[["property_type", "district", "size",
                       "bedrooms", "bathrooms", "price", "compound"]]
    except Exception:
        return df.head(top_n)
