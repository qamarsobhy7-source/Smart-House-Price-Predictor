"""Smart House Price Predictor - Real Data Model (v7.0)"""
from pathlib import Path
import re
import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "real_model.joblib"
METADATA_PATH = MODELS_DIR / "real_model_metadata.joblib"
MAPPINGS_PATH = MODELS_DIR / "real_feature_mappings.joblib"


# NLP keywords for property titles
NLP_KEYWORDS = {
    "nlp_sea_view":     ["sea view", "ocean view", "waterfront", "beach"],
    "nlp_garden":       ["garden", "green"],
    "nlp_duplex":       ["duplex"],
    "nlp_roof":         ["roof", "penthouse"],
    "nlp_furnished":    ["furnished"],
    "nlp_new":          ["new", "brand new", "modern"],
    "nlp_luxury":       ["luxury", "luxurious", "super lux", "high-end", "premium"],
    "nlp_open_view":    ["open view", "panoramic", "scenic"],
    "nlp_parking":      ["parking", "garage"],
    "nlp_elevator":     ["elevator", "lift"],
    "nlp_payment_plan": ["plan", "installment", "years plan"],
    "nlp_ready":        ["ready", "rtm", "move"],
}


# Amenity codes (from PropertyFinder)
AMENITY_CODES = [
    "balcony", "builtin_wardrobes", "covered_parking", "private_garden",
    "shared_pool", "view", "security", "shared_spa", "study", "wc",
    "balcony_2", "lobby", "children_area", "air_conditioning", "kitchen",
    "maid_room", "storage", "dining_area", "annex", "cafeteria",
    "gazebo", "playground", "gym", "elevator", "chiller",
    "furnished", "fully_furnished", "garden", "sport", "shops",
    "park", "mosque",
]


def load_artifacts():
    """Load model, metadata, and mappings."""
    for path in [MODEL_PATH, METADATA_PATH, MAPPINGS_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    mappings = joblib.load(MAPPINGS_PATH)
    return model, metadata, mappings


def get_category_values(mappings):
    """Return categorical values for dropdowns."""
    return mappings["categorical_values"]


def extract_nlp_features(text: str) -> dict:
    """Extract NLP features from title."""
    if not text:
        text = ""
    text_lower = str(text).lower()

    features = {}
    for feat_name, keywords in NLP_KEYWORDS.items():
        pattern = "|".join(map(re.escape, keywords))
        features[feat_name] = int(bool(re.search(pattern, text_lower, re.IGNORECASE)))

    features["title_length"] = len(text_lower)
    features["title_word_count"] = len(text_lower.split())
    return features


def validate_input(area, bedrooms, bathrooms, city, district, compound,
                   price=None):
    """Validate user input."""
    errors = []

    try:
        area_val = float(area)
        if not np.isfinite(area_val) or area_val <= 0:
            errors.append("Area must be a positive number.")
        elif area_val < 80 or area_val > 500:
            errors.append("Area must be between 80 and 500 sqm.")
    except (TypeError, ValueError):
        errors.append("Area is invalid.")

    if str(bedrooms).lower() != "studio":
        try:
            bd = int(bedrooms)
            if bd < 1 or bd > 6:
                errors.append("Bedrooms must be between 1 and 6.")
        except (TypeError, ValueError):
            errors.append("Bedrooms value is invalid.")

    try:
        ba = int(bathrooms)
        if ba < 1 or ba > 5:
            errors.append("Bathrooms must be between 1 and 5.")
    except (TypeError, ValueError):
        errors.append("Bathrooms value is invalid.")

    required = {"City": city, "District": district}
    for label, value in required.items():
        if value is None or not str(value).strip():
            errors.append(f"{label} is required.")

    return errors


def build_features(area, bedrooms, bathrooms, city, district,
                   compound="None", latitude=30.0444, longitude=31.2357,
                   amenities=None, description="", mappings=None):
    """Build feature vector matching real model training schema."""

    if mappings is None:
        _, _, mappings = load_artifacts()

    # Base values
    area = float(area)
    is_studio = 1 if str(bedrooms).lower() == "studio" else 0
    bedrooms_val = 0 if is_studio else int(bedrooms)
    bathrooms_val = int(bathrooms)

    # Interaction features
    log_size = np.log1p(area)
    sqrt_size = np.sqrt(area)
    bed_bath_ratio = bedrooms_val / (bathrooms_val + 1)
    area_per_bedroom = area / (bedrooms_val + 1)
    area_per_bathroom = area / (bathrooms_val + 1)
    rooms_total = bedrooms_val + bathrooms_val
    area_per_room = area / (rooms_total + 1)
    bed_per_sqm = bedrooms_val / area if area > 0 else 0
    bath_per_sqm = bathrooms_val / area if area > 0 else 0

    # GPS-based features
    distance_to_cairo = np.sqrt(
        (latitude - 30.0444) ** 2 + (longitude - 31.2357) ** 2
    )

    # Location pricing (from mappings)
    price_map = mappings["price_mappings"]
    city_ppm = price_map["city_price_per_sqm"].get(city, price_map["global_mean_ppm"])
    district_ppm = price_map["district_price_per_sqm"].get(district, city_ppm)
    compound_ppm = price_map["compound_price_per_sqm"].get(compound, district_ppm)

    # NLP features
    nlp = extract_nlp_features(description)

    # Amenities (list of strings like ['BA', 'SE'])
    if amenities is None:
        amenities = []

    data = {
        # Numerical core
        "latitude": float(latitude),
        "longitude": float(longitude),
        "bedrooms": bedrooms_val,
        "bathrooms": bathrooms_val,
        "size": area,
        "log_size": log_size,
        "sqrt_size": sqrt_size,
        "bed_bath_ratio": bed_bath_ratio,
        "area_per_bedroom": area_per_bedroom,
        "area_per_bathroom": area_per_bathroom,
        "rooms_total": rooms_total,
        "area_per_room": area_per_room,
        "bed_per_sqm": bed_per_sqm,
        "bath_per_sqm": bath_per_sqm,
        "distance_to_cairo": float(distance_to_cairo),
        "geo_cluster": 0,  # default cluster (will be computed ideally)
        "amenity_count": len(amenities),
        # Categorical
        "city": str(city),
        "district": str(district),
        "compound": str(compound),
    }

    # Add all amenity flags
    for code in AMENITY_CODES:
        # Map code to feature name pattern
        feature_name = f"amenity_{code}"
        # Check if this amenity is in the user's list
        # Note: user provides codes like 'BA', 'SE'; we need to match
        data[feature_name] = 0

    # Merge NLP
    data.update(nlp)

    # Filter to only the features model was trained on
    df_out = pd.DataFrame([data])

    # Use metadata to select only the right columns (if loaded from mappings)
    if mappings is not None:
        try:
            _, meta, _ = load_artifacts()
            expected = set(meta['features']['numerical'] + meta['features']['categorical'])
            # Keep only expected columns
            df_out = df_out[[c for c in df_out.columns if c in expected]]

            # Add any missing columns as 0
            for col in expected:
                if col not in df_out.columns:
                    df_out[col] = 0

            # Reorder to match metadata order
            ordered = meta['features']['numerical'] + meta['features']['categorical']
            df_out = df_out[[c for c in ordered if c in df_out.columns]]
        except Exception:
            pass

    return df_out


def predict_price(model, input_data):
    """Predict price and return safe positive value."""
    log_price = float(model.predict(input_data)[0])
    if not np.isfinite(log_price):
        raise ValueError("Model returned invalid prediction.")
    return max(0.0, float(np.expm1(log_price)))


def predict_with_confidence(model, input_data, mape):
    """Predict with confidence interval."""
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
# ROI + Comparison (kept from previous version)
# ==========================================================
def calculate_roi(purchase_price, years=5, monthly_rent_pct=0.005,
                   annual_appreciation=0.12):
    monthly_rent = purchase_price * monthly_rent_pct
    rental_income = monthly_rent * 12 * years
    future_value = purchase_price * ((1 + annual_appreciation) ** years)
    appreciation_gain = future_value - purchase_price
    total_return = rental_income + appreciation_gain
    roi_pct = (total_return / purchase_price) * 100
    annualized_roi = ((1 + total_return / purchase_price) ** (1 / years) - 1) * 100
    return {
        'purchase_price': purchase_price, 'years': years,
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
# Recommendation System
# ==========================================================
_recommendation_data = None


def load_recommendation_data():
    """Lazy load recommendation dataset."""
    global _recommendation_data
    if _recommendation_data is None:
        path = BASE_DIR / "data" / "real_data" / "model_ready_clean.csv"
        if path.exists():
            import pandas as pd
            df = pd.read_csv(path)
            # Prepare reference features
            df['log_size'] = np.log1p(df['size'])
            df['sqrt_size'] = np.sqrt(df['size'])
            df['bed_per_sqm'] = df['bedrooms'] / df['size']
            df['bath_per_sqm'] = df['bathrooms'] / df['size']
            _recommendation_data = df
    return _recommendation_data


def recommend_similar_properties(area, bedrooms, bathrooms, city,
                                   district, compound, top_n=5,
                                   price_range=None):
    """Find top N similar properties from the dataset.

    Args:
        price_range: optional tuple (min_price, max_price) to filter
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity

    df = load_recommendation_data()
    if df is None or len(df) == 0:
        return []

    sim_cols = ['size', 'bedrooms', 'bathrooms', 'latitude', 'longitude']
    for c in sim_cols:
        if c not in df.columns:
            return []

    # Filter by city
    city_df = df[df['city'] == city].copy()
    if len(city_df) < top_n * 4:
        city_df = df.copy()

    # Filter by price range (progressive widening if not enough results)
    if price_range is not None:
        pmin, pmax = price_range
        span = pmax - pmin
        center = (pmin + pmax) / 2

        # Try original range first
        price_filtered = city_df[
            (city_df['price'] >= pmin) & (city_df['price'] <= pmax)
        ]

        # Widen progressively if not enough results
        factor = 1.0
        while len(price_filtered) < top_n and factor < 3.0:
            factor += 0.3
            pmin_w = center - (span * factor / 2)
            pmax_w = center + (span * factor / 2)
            price_filtered = city_df[
                (city_df['price'] >= pmin_w) & (city_df['price'] <= pmax_w)
            ]

        if len(price_filtered) >= top_n:
            city_df = price_filtered
        elif len(price_filtered) > 0:
            city_df = price_filtered

    # Build query
    is_studio = 1 if str(bedrooms).lower() == "studio" else 0
    bedrooms_val = 0 if is_studio else int(bedrooms)
    bathrooms_val = int(bathrooms)

    scaler = StandardScaler()
    X_ref = scaler.fit_transform(city_df[sim_cols].fillna(0))

    query_gps = city_df[['latitude', 'longitude']].median().values
    query = np.array([[float(area), bedrooms_val, bathrooms_val,
                       query_gps[0], query_gps[1]]])
    X_query = scaler.transform(query)

    sims = cosine_similarity(X_query, X_ref)[0]
    top_idx = sims.argsort()[-top_n:][::-1]

    results = []
    seen_keys = set()

    for idx in top_idx:
        row = city_df.iloc[idx].copy()

        # Deduplicate by (area, price, district)
        dedup_key = (
            round(float(row['size'])),
            round(float(row['price']) / 10000),  # round to nearest 10K
            str(row['district']),
        )
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        results.append({
            'area_value': float(row['size']),
            'bedrooms_clean': int(row['bedrooms']) if not pd.isna(row['bedrooms']) else 0,
            'bathrooms_clean': int(row['bathrooms']) if not pd.isna(row['bathrooms']) else 1,
            'city': str(row['city']),
            'district': str(row['district']),
            'compound': str(row['compound']) if 'compound' in row else '',
            'predicted_price': float(row['price']),
            'similarity': float(sims[idx]),
            'is_studio': int(row['bedrooms'] == 0) if not pd.isna(row['bedrooms']) else 0,
        })

        if len(results) >= top_n:
            break

    return results


def compare_properties(model, mappings, prop_a, prop_b):
    """Compare two properties side by side.

    Args:
        prop_a, prop_b: dicts with area, bedrooms, bathrooms, city,
                        district, compound

    Returns:
        dict with prices, per-sqm, cheaper, better_value
    """
    def _predict(p):
        feat = build_features(
            area=p['area'], bedrooms=p['bedrooms'], bathrooms=p['bathrooms'],
            city=p['city'], district=p['district'],
            compound=p.get('compound', 'None'),
            amenities=p.get('amenities', []),
            mappings=mappings,
        )
        price = predict_price(model, feat)
        return price, price / float(p['area'])

    price_a, ppm_a = _predict(prop_a)
    price_b, ppm_b = _predict(prop_b)

    return {
        'property_a': {'price': price_a, 'price_per_sqm': ppm_a},
        'property_b': {'price': price_b, 'price_per_sqm': ppm_b},
        'cheaper': 'A' if price_a < price_b else 'B',
        'better_value': 'A' if ppm_a < ppm_b else 'B',
        'price_diff': abs(price_a - price_b),
        'ppm_diff': abs(ppm_a - ppm_b),
    }
