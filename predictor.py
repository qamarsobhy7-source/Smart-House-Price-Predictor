from pathlib import Path

import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "egypt_real_estate_price_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.joblib"


FEATURE_COLUMNS = [
    "area_value",
    "bedrooms_clean",
    "bathrooms_clean",
    "is_studio",
    "has_reception",
    "has_living",
    "has_kitchen",
    "city",
    "town",
    "district",
    "subdistrict",
    "furnished",
    "completion_status",
]


NUMERIC_FEATURES = [
    "area_value",
    "bedrooms_clean",
    "bathrooms_clean",
    "is_studio",
    "has_reception",
    "has_living",
    "has_kitchen",
]


CATEGORICAL_FEATURES = [
    "city",
    "town",
    "district",
    "subdistrict",
    "furnished",
    "completion_status",
]


def load_artifacts():
    """Load the trained model and metadata."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)

    return model, metadata


def get_category_values(model):
    """Return categorical values learned during training."""

    preprocessor = model.named_steps["preprocessor"]
    cat_pipeline = preprocessor.named_transformers_["cat"]
    encoder = cat_pipeline.named_steps["onehot"]

    categories = {}

    for feature_name, values in zip(
        CATEGORICAL_FEATURES,
        encoder.categories_,
    ):
        categories[feature_name] = [
            str(value) for value in values
        ]

    return categories


def validate_prediction_input(
    area,
    bedrooms,
    bathrooms,
    city,
    town,
    district,
    subdistrict,
    furnished,
    completion_status,
):
    """Validate prediction inputs."""

    errors = []

    try:
        area_value = float(area)
    except (TypeError, ValueError):
        area_value = None

    if area_value is None or not np.isfinite(area_value) or area_value <= 0:
        errors.append("Area must be a positive number.")

    try:
        bathroom_value = int(bathrooms)
    except (TypeError, ValueError):
        bathroom_value = None

    if bathroom_value is None or bathroom_value < 1:
        errors.append("Bathrooms must be at least 1.")

    if bedrooms not in {"studio", "1", "2", "3", "4", "5"}:
        errors.append("Please select a valid bedroom option.")

    required_values = {
        "City": city,
        "Town": town,
        "District": district,
        "Subdistrict": subdistrict,
        "Furnished status": furnished,
        "Completion status": completion_status,
    }

    for label, value in required_values.items():
        if value is None or not str(value).strip():
            errors.append(f"{label} is required.")

    return errors


def build_features(
    area,
    bedrooms,
    bathrooms,
    city,
    town,
    district,
    subdistrict,
    furnished,
    completion_status,
    has_reception=False,
    has_living=False,
    has_kitchen=False,
):
    """Build the exact DataFrame expected by the trained pipeline."""

    is_studio = int(str(bedrooms).lower() == "studio")

    bedrooms_clean = (
        None
        if is_studio
        else int(bedrooms)
    )

    data = {
        "area_value": float(area),
        "bedrooms_clean": bedrooms_clean,
        "bathrooms_clean": int(bathrooms),
        "is_studio": is_studio,
        "has_reception": int(bool(has_reception)),
        "has_living": int(bool(has_living)),
        "has_kitchen": int(bool(has_kitchen)),
        "city": str(city),
        "town": str(town),
        "district": str(district),
        "subdistrict": str(subdistrict),
        "furnished": str(furnished),
        "completion_status": str(completion_status),
    }

    return pd.DataFrame(
        [data],
        columns=FEATURE_COLUMNS,
    )


def predict_price(model, input_data):
    """Generate a safe non-negative prediction."""

    prediction = float(model.predict(input_data)[0])

    if not np.isfinite(prediction):
        raise ValueError("The model returned an invalid prediction.")

    return max(0.0, prediction)


def format_price(price):
    """Format a prediction as Egyptian pounds."""

    return f"{price:,.0f} EGP"
