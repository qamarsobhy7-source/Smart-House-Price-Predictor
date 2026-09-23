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
NLP_KEYWORDS = {
    "nlp_sea_view":     ["sea view", "ocean view", "waterfront", "sea"],
    "nlp_garden":       ["garden", "backyard", "green"],
    "nlp_duplex":       ["duplex"],
    "nlp_roof":         ["roof", "penthouse"],
    "nlp_furnished":    ["furnished"],
    "nlp_new":          ["new", "brand new", "modern"],
    "nlp_super_lux":    ["luxury", "luxurious", "super lux", "high-end", "premium"],
    "nlp_open_view":    ["open view", "panoramic", "scenic"],
    "nlp_parking":      ["parking", "garage"],
    "nlp_elevator":     ["elevator", "lift"],
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
    """Extract boolean features from property description."""
    if not description:
        description = ""
    text = str(description).lower()

    features = {}
    for feature_name, keywords in NLP_KEYWORDS.items():
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


# ==========================================================
# Recommendation System
# ==========================================================
_recommendation_data = None


def load_recommendation_data():
    """Lazy load recommendation dataset."""
    global _recommendation_data
    if _recommendation_data is None:
        path = MODELS_DIR / "recommendation_data.joblib"
        if path.exists():
            _recommendation_data = joblib.load(path)
    return _recommendation_data


def recommend_similar_properties(area, bedrooms, bathrooms, city, town,
                                  district, subdistrict, furnished,
                                  completion_status, top_n=5):
    """Find top N similar properties from the dataset."""
    from sklearn.metrics.pairwise import cosine_similarity

    rec_data = load_recommendation_data()
    if rec_data is None:
        return []

    import pandas as pd
    is_studio = 1 if str(bedrooms).lower() == "studio" else 0
    bedrooms_clean = 0 if is_studio else int(bedrooms)

    # Build query
    query_df = pd.DataFrame([{
        'area_value': float(area),
        'bedrooms_clean': bedrooms_clean,
        'bathrooms_clean': int(bathrooms),
        'is_studio': is_studio,
        'city': str(city),
        'town': str(town),
        'district': str(district),
        'subdistrict': str(subdistrict),
        'furnished': str(furnished),
        'completion_status': str(completion_status),
    }])

    # Fill any missing numerical columns with 0
    for col in rec_data['numerical']:
        if col not in query_df.columns:
            query_df[col] = 0

    query_encoded = rec_data['preprocessor'].transform(
        query_df[rec_data['numerical'] + rec_data['categorical']]
    )

    # Similarity
    sims = cosine_similarity(query_encoded, rec_data['X_rec'])[0]
    top_idx = sims.argsort()[-top_n:][::-1]

    results = []
    for idx in top_idx:
        prop = rec_data['df'][idx].copy()
        prop['similarity'] = float(sims[idx])
        results.append(prop)

    return results


# ==========================================================
# Investment ROI Calculator
# ==========================================================
def calculate_roi(purchase_price, years=5, monthly_rent_pct=0.005,
                   annual_appreciation=0.12):
    """Calculate investment ROI.

    Args:
        purchase_price: property price in EGP
        years: investment horizon
        monthly_rent_pct: monthly rent as fraction of purchase price
        annual_appreciation: annual price appreciation rate

    Returns:
        dict with rental_income, future_value, total_return, roi_pct, irr_estimate
    """
    monthly_rent = purchase_price * monthly_rent_pct
    rental_income = monthly_rent * 12 * years
    future_value = purchase_price * ((1 + annual_appreciation) ** years)
    appreciation_gain = future_value - purchase_price
    total_return = rental_income + appreciation_gain
    roi_pct = (total_return / purchase_price) * 100

    # Simple annualized ROI
    annualized_roi = ((1 + total_return / purchase_price) ** (1 / years) - 1) * 100

    return {
        'purchase_price': purchase_price,
        'years': years,
        'monthly_rent': monthly_rent,
        'annual_rental_income': monthly_rent * 12,
        'total_rental_income': rental_income,
        'future_value': future_value,
        'appreciation_gain': appreciation_gain,
        'total_return': total_return,
        'roi_pct': roi_pct,
        'annualized_roi_pct': annualized_roi,
    }


# ==========================================================
# Property Comparison
# ==========================================================
def compare_properties(model, mappings, prop_a, prop_b):
    """Compare two properties side by side.

    Args:
        prop_a, prop_b: dicts with area, bedrooms, bathrooms, city, town,
                        district, subdistrict, furnished, completion_status

    Returns:
        dict with prices, per-sqm, cheaper, better_value
    """
    def _predict(p):
        feat = build_features(
            area=p['area'], bedrooms=p['bedrooms'], bathrooms=p['bathrooms'],
            city=p['city'], town=p['town'], district=p['district'],
            subdistrict=p['subdistrict'], furnished=p['furnished'],
            completion_status=p['completion_status'], mappings=mappings,
        )
        price = predict_price(model, feat)
        return price, price / float(p['area'])

    price_a, ppm_a = _predict(prop_a)
    price_b, ppm_b = _predict(prop_b)

    cheaper = 'A' if price_a < price_b else 'B'
    better_value = 'A' if ppm_a < ppm_b else 'B'

    return {
        'property_a': {'price': price_a, 'price_per_sqm': ppm_a},
        'property_b': {'price': price_b, 'price_per_sqm': ppm_b},
        'cheaper': cheaper,
        'better_value': better_value,
        'price_diff': abs(price_a - price_b),
        'ppm_diff': abs(ppm_a - ppm_b),
    }
