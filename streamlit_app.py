
import streamlit as st
import joblib
import pandas as pd
from pathlib import Path


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "egypt_real_estate_price_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.joblib"


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    return model, metadata


model, metadata = load_model()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Egypt Real Estate Price Predictor",
    page_icon="🏠",
    layout="centered"
)


# ============================================================
# HEADER
# ============================================================

st.title("🏠 Egypt Real Estate Price Predictor")

st.write(
    "Estimate the sale price of a residential apartment in Egypt "
    "using a machine learning model trained on real estate data."
)

st.divider()


# ============================================================
# PROPERTY DETAILS
# ============================================================

st.subheader("Property Details")

area = st.number_input(
    "Area (m²)",
    min_value=1.0,
    max_value=1000.0,
    value=150.0,
    step=1.0
)

bedroom_option = st.selectbox(
    "Bedrooms",
    ["1", "2", "3", "4", "5", "studio"]
)

bathrooms = st.number_input(
    "Bathrooms",
    min_value=1,
    max_value=10,
    value=2,
    step=1
)


# ============================================================
# LOCATION
# ============================================================

st.subheader("Location")

city = st.selectbox(
    "City",
    [
        "Cairo",
        "Giza",
        "Alexandria",
        "Red Sea",
        "North Coast",
        "Suez"
    ]
)

town = st.text_input(
    "Town",
    value="New Cairo City"
)

district = st.text_input(
    "District",
    value="The 5th Settlement"
)

subdistrict = st.text_input(
    "Subdistrict",
    value="5th Settlement Compounds"
)


# ============================================================
# PROPERTY STATUS
# ============================================================

st.subheader("Property Status")

furnished = st.selectbox(
    "Furnished Status",
    ["YES", "NO", "Unknown"]
)

completion_status = st.selectbox(
    "Completion Status",
    [
        "completed",
        "off_plan_primary",
        "off_plan",
        "completed_primary"
    ]
)


# ============================================================
# PROPERTY FEATURES
# ============================================================

st.subheader("Property Features")

has_reception = st.checkbox("Reception Area")
has_living = st.checkbox("Living Area")
has_kitchen = st.checkbox("Kitchen")


# ============================================================
# PREDICTION
# ============================================================

if st.button("Estimate Property Price", type="primary"):

    is_studio = int(bedroom_option == "studio")

    bedrooms_clean = (
        None if is_studio else int(bedroom_option)
    )

    input_data = pd.DataFrame([{
        "area_value": area,
        "bedrooms_clean": bedrooms_clean,
        "bathrooms_clean": bathrooms,
        "is_studio": is_studio,
        "has_reception": int(has_reception),
        "has_living": int(has_living),
        "has_kitchen": int(has_kitchen),
        "city": city,
        "town": town,
        "district": district,
        "subdistrict": subdistrict,
        "furnished": furnished,
        "completion_status": completion_status
    }])

    try:
        predicted_price = float(model.predict(input_data)[0])
        predicted_price = max(0, predicted_price)

        st.success(
            f"Estimated Property Price: {predicted_price:,.0f} EGP"
        )

    except Exception as error:
        st.error(
            "An error occurred while generating the prediction."
        )
        st.exception(error)


# ============================================================
# MODEL INFORMATION
# ============================================================

with st.expander("Model Information"):

    st.write(
        f"**Model:** "
        f"{metadata.get('model_type', 'Unknown')}"
    )

    st.write(
        f"**Target:** "
        f"{metadata.get('target', 'Unknown')}"
    )

    st.write(
        f"**Features:** "
        f"{metadata.get('feature_count', 13)}"
    )

    st.caption(
        "The prediction is an estimate and should not be considered "
        "a professional property valuation."
    )
