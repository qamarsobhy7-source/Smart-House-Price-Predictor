"""
Smart House Price Predictor — v9 Adapter (COMPLETE)
Provides ALL keys required by original streamlit_app.py
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
    """Load model + metadata + mappings (with ALL required keys)."""
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    cat_features = joblib.load(CAT_FEATURES_PATH)

    # ✅ metadata with ALL required keys
    metadata = {
        "model_name": "CatBoost",
        "model_version": "v9",
        
        # Metrics (used by hero section)
        "metrics": {
            "r2": 0.7061,
            "mape": 40.52,
            "mae": 4825050,
            "rmse": 10300000,
        },
        
        # Training info (used by hero section)
        "training_info": {
            "n_total": 119916,
            "n_train": 95932,
            "n_test": 23984,
            "trained_at": "2026-01-15",
            "algorithm": "CatBoost",
            "n_features": len(features),
        },
        
        # Legacy keys
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

    # ✅ mappings with price_mappings
    try:
        df = pd.read_csv(BASE_DIR / "data" / "processed" / "FINAL_DATASET_v9.csv")
        
        # Categorical values
        categorical_values = {}
        for col in cat_features:
            categorical_values[col] = sorted(df[col].dropna().astype(str).unique().tolist())
        
        # Price mappings (median price per category)
        price_mappings = {
            "by_governorate": df.groupby("governorate")["price"].median().to_dict(),
            "by_property_type": df.groupby("property_type")["price"].median().to_dict(),
            "by_district": df.groupby("district")["price"].median().to_dict(),
            "by_compound": df.groupby("compound")["price"].median().to_dict(),
            "global_median": float(df["price"].median()),
            "global_mean": float(df["price"].mean()),
        }
    except Exception as e:
        print(f"⚠️ Warning: {e}")
        categorical_values = {
            "property_type": ["Apartment", "Villa", "Townhouse", "Duplex",
                              "Penthouse", "Twin House", "iVilla",
                              "Hotel Apartment", "Chalet"],
            "governorate": ["Cairo", "Giza", "Matrouh", "Red Sea",
                            "Alexandria", "Suez"],
        }
        price_mappings = {
            "by_governorate": {},
            "by_property_type": {},
            "global_median": 12000000,
            "global_mean": 18000000,
        }

    mappings = {
        "categorical_values": categorical_values,
        "price_mappings": price_mappings,
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
def validate_input(area, bedrooms, bathrooms, city, district, compound, price=None):
    """Validate user input."""
    errors = []
    try:
        area_val = float(area)
        if not np.isfinite(area_val) or area_val <= 0:
            errors.append("Area must be positive.")
        elif area_val < 20 or area_val > 5000:
            errors.append("Area must be 20-5000 sqm.")
    except (TypeError, ValueError):
        errors.append("Area invalid.")

    try:
        bd = int(bedrooms)
        if bd < 0 or bd > 15:
            errors.append("Bedrooms 0-15.")
    except (TypeError, ValueError):
        errors.append("Bedrooms invalid.")

    try:
        ba = int(bathrooms)
        if ba < 1 or ba > 15:
            errors.append("Bathrooms 1-15.")
    except (TypeError, ValueError):
        errors.append("Bathrooms invalid.")

    return errors


# ═══════════════════════════════════════════════════════
# BUILD FEATURES
# ═══════════════════════════════════════════════════════
def build_features(input_dict, features, cat_features):
    """Build feature vector."""
    row = {}
    for f in features:
        if f in cat_features:
            row[f] = str(input_dict.get(f, "Unknown"))
        else:
            row[f] = float(input_dict.get(f, 0))
    return pd.DataFrame([row])[features]


# ═══════════════════════════════════════════════════════
# PREDICT WITH CONFIDENCE
# ═══════════════════════════════════════════════════════
def predict_with_confidence(model, X, features, cat_features):
    """Predict + confidence interval."""
    try:
        log_price = model.predict(X)[0]
        price = float(np.expm1(log_price))
        mape = 0.4052
        return {
            "price": price,
            "price_low": price * (1 - mape),
            "price_high": price * (1 + mape),
            "confidence": 0.71,
            "log_price": float(log_price),
        }
    except Exception as e:
        return {"error": str(e), "price": 0}


# ═══════════════════════════════════════════════════════
# FORMAT PRICE
# ═══════════════════════════════════════════════════════
def format_price(price, lang="en"):
    """Format price."""
    if price >= 1_000_000:
        m = price / 1_000_000
        return f"{m:.2f} مليون جنيه" if lang == "ar" else f"EGP {m:.2f}M"
    elif price >= 1_000:
        k = price / 1_000
        return f"{k:.0f} ألف جنيه" if lang == "ar" else f"EGP {k:.0f}K"
    return f"EGP {price:,.0f}"


# ═══════════════════════════════════════════════════════
# ROI
# ═══════════════════════════════════════════════════════
def calculate_roi(price, years=5, growth_rate=0.08):
    """Calculate ROI."""
    future = price * ((1 + growth_rate) ** years)
    return {
        "current_price": price,
        "future_price": future,
        "roi_percent": ((future - price) / price) * 100,
        "gain": future - price,
        "years": years,
    }


# ═══════════════════════════════════════════════════════
# SIMILAR PROPERTIES
# ═══════════════════════════════════════════════════════
def recommend_similar_properties(df, governorate, property_type, size, price, top_n=3):
    """Find similar."""
    try:
        filtered = df[
            (df["governorate"] == governorate) &
            (df["property_type"] == property_type) &
            (df["size"].between(size * 0.8, size * 1.2))
        ].copy()
        if len(filtered) == 0:
            filtered = df[df["governorate"] == governorate].head(top_n)
        filtered["price_diff"] = abs(filtered["price"] - price)
        return filtered.nsmallest(top_n, "price_diff")[
            ["property_type", "district", "size", "bedrooms", "bathrooms", "price", "compound"]
        ]
    except Exception:
        return df.head(top_n)
