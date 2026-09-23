"""Smart House Price Predictor - Streamlit UI v3.0 (English)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import shap
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_price, predict_with_confidence, format_price,
)

st.set_page_config(page_title="Smart House Price Predictor",
                   page_icon="🏠", layout="wide")

st.markdown("""
<style>
.main-title {font-size:2.5rem; font-weight:800; text-align:center;
  background:linear-gradient(90deg,#1E88E5,#43A047);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.subtitle {text-align:center; color:#666; font-size:1.05rem; margin-bottom:1.5rem;}
.price-card {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  padding:2rem; border-radius:1rem; color:white; text-align:center;
  box-shadow:0 10px 30px rgba(0,0,0,0.15); margin:1rem 0;}
.price-value {font-size:3rem; font-weight:900; margin:0.5rem 0;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def _load():
    return load_artifacts()


try:
    model, metadata, mappings = _load()
    categories = get_category_values(mappings)
except Exception as e:
    st.error(f"Model loading error: {e}")
    st.stop()

st.markdown('<h1 class="main-title">🏠 Smart House Price Predictor</h1>',
            unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-powered property price prediction for the Egyptian real estate market</p>',
            unsafe_allow_html=True)


# ============================================================
# Sidebar - Inputs
# ============================================================
with st.sidebar:
    st.header("Property Details")
    area = st.slider("Area (m²)", 40, 500, 150, 5)
    bedrooms = st.selectbox("Bedrooms", ["studio","1","2","3","4","5","6"])
    bathrooms = st.slider("Bathrooms", 1, 5, 2)

    st.divider()
    st.subheader("Location")
    city = st.selectbox("City", categories["city"])
    town = st.selectbox("Town", categories["town"])
    district = st.selectbox("District", categories["district"])
    subdistrict = st.selectbox("Subdistrict", categories["subdistrict"])

    st.divider()
    st.subheader("Status")
    furnished = st.selectbox("Furnished", categories["furnished"])
    completion_status = st.selectbox("Completion Status",
                                      categories["completion_status"])

    st.divider()
    st.subheader("Features")
    has_reception = st.checkbox("Reception Area", True)
    has_living = st.checkbox("Living Area", True)
    has_kitchen = st.checkbox("Kitchen", True)

    st.divider()
    description = st.text_area("Description (Arabic or English)",
        height=80, placeholder="e.g., شقة بحرية مفروشة سوبر لوكس")
    predict_btn = st.button("Predict Price", type="primary",
                            use_container_width=True)


# ============================================================
# Top Metrics
# ============================================================
m = metadata["metrics"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("R² Score", f"{m['r2']:.4f}")
c2.metric("MAPE", f"{m['mape']:.2f}%")
c3.metric("MAE", f"{m['mae']:,.0f} EGP")
c4.metric("Features", metadata["features"]["total"])


# ============================================================
# Build features once
# ============================================================
input_features = build_features(
    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
    city=city, town=town, district=district, subdistrict=subdistrict,
    furnished=furnished, completion_status=completion_status,
    has_reception=has_reception, has_living=has_living,
    has_kitchen=has_kitchen, description=description, mappings=mappings,
)


# ============================================================
# Tabs
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Prediction", "🔍 Explanation", "🗺️ Price Map", "🎛️ What-If"
])


# ---------- Tab 1: Prediction ----------
with tab1:
    if predict_btn:
        errors = validate_input(area, bedrooms, bathrooms, city, town,
                                 district, subdistrict, furnished,
                                 completion_status)
        if errors:
            st.error(" | ".join(errors))
        else:
            result = predict_with_confidence(model, input_features, m["mape"])
            price = result["price"]

            st.markdown(f"""
            <div class="price-card">
                <h2>Estimated Price</h2>
                <div class="price-value">{price/1_000_000:.2f}M EGP</div>
                <div style="font-size:1.3rem">{price:,.0f} EGP</div>
                <div style="margin-top:1rem;opacity:0.9;">
                    Confidence Range: {format_price(result['lower_bound'])} — {format_price(result['upper_bound'])}
                </div>
            </div>""", unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Price per m²", f"{price/area:,.0f} EGP")
            col_b.metric("District Avg",
                         f"{mappings['price_mappings']['district_price_per_sqm'].get(district,0):,.0f} EGP/m²")
            col_c.metric("Model Accuracy", f"{100-m['mape']:.1f}%")
    else:
        st.info("👈 Configure the property in the sidebar and click **Predict Price**")


# ---------- Tab 2: SHAP Explanation ----------
with tab2:
    st.subheader("Why this price? (SHAP Feature Contributions)")
    st.caption("Shows how each feature pushes the prediction up (green) or down (red)")

    @st.cache_resource
    def _shap_explainer(_model):
        inner = _model.named_steps['model']
        return shap.TreeExplainer(inner)

    try:
        prep = model.named_steps['prep']
        X_t = prep.transform(input_features)
        feat_names = prep.get_feature_names_out()
        explainer = _shap_explainer(model)
        sv = explainer.shap_values(X_t)
        sv_flat = np.array(sv).flatten()

        top_n = 12
        idx = np.argsort(np.abs(sv_flat))[-top_n:][::-1]
        colors = ['#43A047' if v > 0 else '#E53935' for v in sv_flat[idx]]

        fig = go.Figure(go.Bar(
            x=sv_flat[idx],
            y=[feat_names[i].replace('num__','').replace('cat__','')
               for i in idx],
            orientation='h',
            marker_color=colors,
            text=[f"{v:+.3f}" for v in sv_flat[idx]],
            textposition='outside',
        ))
        fig.update_layout(
            title=f"Top {top_n} Feature Contributions (log-price space)",
            height=520, margin=dict(l=20, r=20, t=60, b=20),
            xaxis_title="SHAP Value (impact on log-price)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        pos = sum(1 for v in sv_flat if v > 0)
        neg = sum(1 for v in sv_flat if v < 0)
        c1, c2 = st.columns(2)
        c1.metric("Features increasing price", pos)
        c2.metric("Features decreasing price", neg)

    except Exception as e:
        st.error(f"SHAP computation error: {e}")


# ---------- Tab 3: Price Map ----------
with tab3:
    st.subheader("Average Price per m² by District")
    st.caption("Hover over any marker to see the average price for that district")

    price_data = mappings["price_mappings"]["district_price_per_sqm"]
    city_centers = {
        "Cairo": (30.0444, 31.2357),
        "Giza": (30.0131, 31.2089),
        "Alexandria": (31.2001, 29.9187),
        "Mansoura": (31.0409, 31.3785),
        "Tanta": (30.7865, 31.0004),
    }

    m_map = folium.Map(location=[30.2, 31.2], zoom_start=7,
                       tiles="cartodbpositron")

    for d_name, ppm in price_data.items():
        h = abs(hash(d_name))
        city_key = list(city_centers.keys())[h % 5]
        lat, lon = city_centers[city_key]
        lat += ((h // 7) % 60 - 30) / 500
        lon += ((h // 13) % 60 - 30) / 500

        color = ('#43A047' if ppm < 25000
                 else '#FB8C00' if ppm < 40000 else '#E53935')
        folium.CircleMarker(
            location=[lat, lon], radius=10, color=color,
            fill=True, fill_opacity=0.75, weight=2,
            popup=folium.Popup(
                f"<b>{d_name}</b><br>Avg: {ppm:,.0f} EGP/m²",
                max_width=200),
        ).add_to(m_map)

    st_folium(m_map, width=None, height=500, returned_objects=[])

    ppm_series = pd.Series(price_data).sort_values(ascending=False)
    fig2 = go.Figure(go.Bar(
        x=ppm_series.values, y=ppm_series.index, orientation='h',
        marker_color=['#E53935' if v > 40000 else '#FB8C00'
                       if v > 25000 else '#43A047' for v in ppm_series.values],
    ))
    fig2.update_layout(title="District Ranking by Avg Price/m²",
                        height=600, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig2, use_container_width=True)


# ---------- Tab 4: What-If Analysis ----------
with tab4:
    st.subheader("What-If Analysis")
    st.caption("Adjust parameters and instantly see the impact on the predicted price")

    base_price = predict_price(model, input_features)
    st.metric("Base Price (current settings)", f"{base_price:,.0f} EGP")

    col1, col2 = st.columns(2)
    with col1:
        delta_area = st.slider("Change Area by (m²)", -100, 200, 0, 10)
    with col2:
        bd_base = 1 if bedrooms == "studio" else int(bedrooms)
        delta_bedrooms = st.slider("Change Bedrooms by", -3, 3, 0)

    new_area = max(40, min(500, area + delta_area))
    new_bedrooms = max(1, min(6, bd_base + delta_bedrooms))

    modified = build_features(
        area=new_area, bedrooms=str(new_bedrooms), bathrooms=bathrooms,
        city=city, town=town, district=district, subdistrict=subdistrict,
        furnished=furnished, completion_status=completion_status,
        has_reception=has_reception, has_living=has_living,
        has_kitchen=has_kitchen, description=description, mappings=mappings,
    )
    new_price = predict_price(model, modified)
    diff = new_price - base_price
    pct = (diff / base_price) * 100 if base_price > 0 else 0

    st.markdown(f"""
    <div class="price-card">
        <h3>New Price</h3>
        <div class="price-value">{new_price/1_000_000:.2f}M EGP</div>
        <div style="font-size:1.3rem">{new_price:,.0f} EGP</div>
        <div style="margin-top:1rem;font-size:1.1rem;">
            Change: {'+' if diff >= 0 else ''}{diff:,.0f} EGP ({pct:+.1f}%)
        </div>
    </div>""", unsafe_allow_html=True)

    comparison = pd.DataFrame({
        "Parameter": ["Area (m²)", "Bedrooms", "Predicted Price (EGP)"],
        "Original": [area, bedrooms, f"{base_price:,.0f}"],
        "Modified": [new_area, str(new_bedrooms), f"{new_price:,.0f}"],
        "Impact": ["—", "—", f"{diff:+,.0f}"],
    })
    st.dataframe(comparison, hide_index=True, use_container_width=True)


# ============================================================
# Footer
# ============================================================
st.divider()
with st.expander("ℹ️ Model Information"):
    st.write(f"**Model:** {metadata['model_name']}")
    st.write(f"**Training samples:** {metadata['training_info']['n_train']:,}")
    st.write(f"**Features:** {metadata['features']['total']}")
    st.write(f"**R²:** {m['r2']:.4f} | **MAPE:** {m['mape']:.2f}%")

st.caption("⚠️ Disclaimer: Educational AI tool. Not a substitute for professional real estate appraisal.")
