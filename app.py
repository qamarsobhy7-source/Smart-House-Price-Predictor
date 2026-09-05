
from flask import Flask, render_template, request
import joblib
import pandas as pd
import os


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "egypt_real_estate_price_model.joblib"
)

METADATA_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_metadata.joblib"
)


# ============================================================
# LOAD MODEL AND METADATA
# ============================================================

try:
    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)

    print("Model loaded successfully.")
    print(f"Model type: {metadata.get('model_type', 'Unknown')}")
    print(f"Target: {metadata.get('target', 'Unknown')}")

except Exception as error:
    model = None
    metadata = None
    print(f"Error loading model: {error}")


# ============================================================
# FEATURE CONFIGURATION
# ============================================================

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
    "completion_status"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_float(value):
    """Convert a form value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_integer(value):
    """Convert a form value to integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def validate_input(data):
    """Validate user input before prediction."""

    errors = []

    area = parse_float(data.get("area"))
    bathrooms = parse_integer(data.get("bathrooms"))

    bedrooms_raw = data.get("bedrooms")

    if area is None or area <= 0:
        errors.append("Area must be a positive number.")

    if bathrooms is None or bathrooms < 1:
        errors.append("Bathrooms must be at least 1.")

    if not bedrooms_raw:
        errors.append("Please select the number of bedrooms.")

    required_text_fields = [
        ("city", "City"),
        ("town", "Town"),
        ("district", "District"),
        ("subdistrict", "Subdistrict"),
        ("furnished", "Furnished status"),
        ("completion_status", "Completion status")
    ]

    for field_name, display_name in required_text_fields:
        if not data.get(field_name):
            errors.append(f"Please select {display_name}.")

    return errors


def build_features(data):
    """
    Convert form data into the exact feature structure
    expected by the trained model.
    """

    bedrooms_raw = data.get("bedrooms")

    is_studio = int(bedrooms_raw == "studio")

    if is_studio:
        bedrooms_clean = None
    else:
        bedrooms_clean = parse_integer(bedrooms_raw)

    features = {
        "area_value": parse_float(data.get("area")),
        "bedrooms_clean": bedrooms_clean,
        "bathrooms_clean": parse_integer(data.get("bathrooms")),
        "is_studio": is_studio,
        "has_reception": int(data.get("has_reception") == "yes"),
        "has_living": int(data.get("has_living") == "yes"),
        "has_kitchen": int(data.get("has_kitchen") == "yes"),
        "city": data.get("city"),
        "town": data.get("town"),
        "district": data.get("district"),
        "subdistrict": data.get("subdistrict"),
        "furnished": data.get("furnished"),
        "completion_status": data.get("completion_status")
    }

    return pd.DataFrame([features], columns=FEATURE_COLUMNS)


def format_price(price):
    """Format predicted price as Egyptian Pounds."""
    return f"{price:,.0f} EGP"


# ============================================================
# ROUTES
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    error_message = None

    form_data = {}

    if request.method == "POST":

        form_data = request.form.to_dict()

        # Validate input
        errors = validate_input(form_data)

        if errors:
            error_message = " ".join(errors)

        elif model is None:
            error_message = (
                "The prediction model could not be loaded. "
                "Please check the model files."
            )

        else:
            try:
                # Build model input
                input_data = build_features(form_data)

                # Generate prediction
                predicted_price = model.predict(input_data)[0]

                # Prevent invalid negative output
                predicted_price = max(0, float(predicted_price))

                # Format result
                prediction = format_price(predicted_price)

            except Exception as error:
                error_message = (
                    "An error occurred while generating the prediction. "
                    "Please check your input and try again."
                )

                print(f"Prediction error: {error}")

    return render_template(
        "index.html",
        prediction=prediction,
        error_message=error_message,
        form_data=form_data
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
