"""
Smart House Price Predictor - v3.0
====================================
Advanced ML system for predicting residential property prices in Egypt.

Features:
- Gradient Boosting Regressor (R² = 0.97)
- 26 engineered features
- SHAP explanations
- Arabic NLP on property descriptions
- Confidence intervals
"""
from pathlib import Path
import re
import joblib
import numpy as np
import pandas as pd


# ==========================================================
# Paths
# ==========================================================
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "house_price_model_v3.joblib"
METADATA_PATH = MODELS_DIR / "house_price_model_v3_metadata.joblib"
MAPPINGS_PATH = MODELS_DIR / "feature_mappings.joblib"


# ==========================================================
# Arabic NLP Keywords
# ==========================================================
ARABIC_KEYWORDS = {
    "nlp_sea_view":     ["بحرية", "بحر", "sea view", "sea"],
    "nlp_garden":       ["حديقة", "garden"],
    "nlp_duplex":       ["دوبلكس", "duplex"],
    "nlp_roof":         ["روف", "roof"],
    "nlp_furnished":    ["مفروش", "furnished"],
    "nlp_new":          ["جديد", "new"],
    "nlp_super_lux":    ["سوبر لوكس", "super lux", "الترا"],
    "nlp_open_view":    ["فيو مفتوح", "open view"],
    "nlp_parking":      ["جراج", "garage", "parking"],
    "nlp_elevator":     ["اسانسير", "مصعد", "elevator"],
}


# ==========================================================
# Load Artifacts
# ==========================================================
def load_artifacts():
    """Load model, metadata, and feature mappings."""
    for path in [MODEL_PATH, METADATA_PATH, MAPPINGS_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    mappings = joblib.load(MAPPINGS_PATH)

    return model, metadata, mappings


def get_category_values(mappings):
    """Return categorical values for UI dropdowns."""
    return mappings["categorical_values"]


# ==========================================================
# Arabic NLP Feature Extraction
# ==========================================================
def extract_nlp_features(description: str) -> dict:
    """Extract boolean features from Arabic/English property description."""
    if not description:
        description = ""
    text = str(description).lower()

    features = {}
    for feature_name, keywords in ARABIC_KEYWORDS.items():
        pattern = "|".join(map(re.escape, keywords))
        features[feature_name] = int(bool(re.search(pattern, text, re.IGNORECASE)))

    features["description_length"] = len(text)
    features["description_word_count"] = len(text.split())

    return features


# ==========================================================
# Input Validation
# ==========================================================
def validate_input(area, bedrooms, bathrooms, city, town, district,
                   subdistrict, furnished, completion_status):
    """Validate user inputs and return list of errors."""
    errors = []

    # Area
    try:
        area_val = float(area)
        if not np.isfinite(area_val) or area_val <= 0:
            errors.append("Area must be a positive number.")
        elif area_val < 30 or area_val > 1000:
            errors.append("Area must be between 30 and 1000 m².")
    except (TypeError, ValueError):
        errors.append("Area is invalid.")

    # Bedrooms
    if str(bedrooms).lower() != "studio":
        try:
            bd = int(bedrooms)
            if bd < 1 or bd > 10:
                errors.append("Bedrooms must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Bedrooms value is invalid.")

    # Bathrooms
    try:
        ba = int(bathrooms)
        if ba < 1 or ba > 10:
            errors.append("Bathrooms must be between 1 and 10.")
    except (TypeError, ValueError):
        errors.append("Bathrooms value is invalid.")

    # Categorical
    required = {
        "City": city,
        "Town": town,
        "District": district,
        "Subdistrict": subdistrict,
        "Furnished status": furnished,
        "Completion status": completion_status,
    }
    for label, value in required.items():
        if value is None or not str(value).strip():
            errors.append(f"{label} is required.")

    return errors


# ==========================================================
# Feature Building
# ==========================================================
def build_features(area, bedrooms, bathrooms, city, town, district,
                   subdistrict, furnished, completion_status,
                   has_reception=False, has_living=False, has_kitchen=False,
                   description="", mappings=None):
    """Build feature DataFrame matching the training schema."""

    if mappings is None:
        _, _, mappings = load_artifacts()

    # Base features
    is_studio = 1 if str(bedrooms).lower() == "studio" else 0
    bedrooms_clean = 0 if is_studio else int(bedrooms)
    bathrooms_clean = int(bathrooms)
    area_value = float(area)

    # Interaction features
    bed_bath_ratio = bedrooms_clean / (bathrooms_clean + 1)
    area_per_bedroom = area_value / (bedrooms_clean + 1)
    area_per_bathroom = area_value / (bathrooms_clean + 1)
    rooms_total = bedrooms_clean + bathrooms_clean
    area_per_room = area_value / (rooms_total + 1)

    # Binary flags
    is_completed = 1 if completion_status == "completed" else 0
    is_under_construction = 1 if completion_status == "under_construction" else 0
    is_off_plan = 1 if completion_status == "off_plan" else 0
    is_furnished = 1 if furnished == "Yes" else 0
    is_semi_furnished = 1 if furnished == "Semi" else 0

    # Location target encoding
    price_map = mappings["price_mappings"]
    global_ppm = price_map["global_mean_ppm"]

    city_ppm = price_map["city_price_per_sqm"].get(str(city), global_ppm)
    town_ppm = price_map["town_price_per_sqm"].get(str(town), city_ppm)
    district_ppm = price_map["district_price_per_sqm"].get(str(district), town_ppm)

    # NLP features
    nlp_features = extract_nlp_features(description)

    data = {
        "area_value": area_value,
        "bedrooms_clean": bedrooms_clean,
        "bathrooms_clean": bathrooms_clean,
        "is_studio": is_studio,
        "has_reception": int(bool(has_reception)),
        "has_living": int(bool(has_living)),
        "has_kitchen": int(bool(has_kitchen)),
        "bed_bath_ratio": bed_bath_ratio,
        "area_per_bedroom": area_per_bedroom,
        "area_per_bathroom": area_per_bathroom,
        "rooms_total": rooms_total,
        "area_per_room": area_per_room,
        "is_completed": is_completed,
        "is_under_construction": is_under_construction,
        "is_off_plan": is_off_plan,
        "is_furnished": is_furnished,
        "is_semi_furnished": is_semi_furnished,
        "city_price_per_sqm": city_ppm,
        "town_price_per_sqm": town_ppm,
        "district_price_per_sqm": district_ppm,
        "city": str(city),
        "town": str(town),
        "district": str(district),
        "subdistrict": str(subdistrict),
        "furnished": str(furnished),
        "completion_status": str(completion_status),
    }

    # Merge NLP features
    data.update(nlp_features)

    return pd.DataFrame([data])


# ==========================================================
# Prediction
# ==========================================================
def predict_price(model, input_data):
    """Predict price and return safe positive value."""
    log_price = float(model.predict(input_data)[0])
    if not np.isfinite(log_price):
        raise ValueError("Model returned invalid prediction.")
    price = float(np.expm1(log_price))
    return max(0.0, price)


def predict_with_confidence(model, input_data, mape):
    """Predict with confidence interval based on MAPE."""
    price = predict_price(model, input_data)
    margin = price * (mape / 100)
    return {
        "price": price,
        "lower_bound": max(0, price - margin),
        "upper_bound": price + margin,
    }


def format_price(price):
    """Format price for display."""
    if price >= 1_000_000:
        return f"{price/1_000_000:.2f}M EGP"
    return f"{price:,.0f} EGP"


# ==========================================================
# SHAP Explainer (lazy loading)
# ==========================================================
_shap_explainer = None


def get_shap_explainer(model, background_data):
    """Get or create SHAP explainer (cached)."""
    global _shap_explainer
    if _shap_explainer is None:
        try:
            import shap
            _shap_explainer = shap.Explainer(
                model.named_steps['model'],
                background_data,
                feature_names=background_data.columns.tolist() if hasattr(background_data, 'columns') else None
            )
        except Exception as e:
            print(f"SHAP initialization error: {e}")
            return None
    return _shap_explainer
