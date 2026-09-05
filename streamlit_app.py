
import streamlit as st

from predictor import (
    load_artifacts,
    get_category_values,
    build_features,
    predict_price,
    format_price,
)
from pathlib import Path


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Egypt Real Estate Price Predictor",
    page_icon="🏠",
    layout="centered"
)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():
    return load_artifacts()


model, metadata = load_model()
category_values = get_category_values(model)


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

town = st.selectbox(
    "Town",
    category_values["town"]
)

district = st.selectbox(
    "District",
    category_values["district"]
)

subdistrict = st.selectbox(
    "Subdistrict",
    category_values["subdistrict"]
)


# ============================================================
# PROPERTY STATUS
# ============================================================

st.subheader("Property Status")

furnished = st.selectbox(
    "Furnished Status",
    category_values["furnished"]
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

    try:
        input_data = build_features(
            area=area,
            bedrooms=bedroom_option,
            bathrooms=bathrooms,
            city=city,
            town=town,
            district=district,
            subdistrict=subdistrict,
            furnished=furnished,
            completion_status=completion_status,
            has_reception=has_reception,
            has_living=has_living,
            has_kitchen=has_kitchen,
        )

        predicted_price = predict_price(model, input_data)

        st.success(
            f"Estimated Property Price: {format_price(predicted_price)}"
        )

    except Exception:
        st.error(
            "Unable to generate the prediction. Please check your inputs and try again."
        )


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

    feature_count = len(metadata.get("features", []))

    st.write(
        f"**Features:** "
        f"{feature_count}"
    )

    st.caption(
        "The prediction is an estimate and should not be considered "
        "a professional property valuation."
    )
