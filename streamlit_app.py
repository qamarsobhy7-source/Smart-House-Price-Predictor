"""Smart House Price Predictor - Modern Streamlit UI v4.0"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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

st.set_page_config(
    page_title="Smart House Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PREMIUM CSS
# ============================================================
st.markdown("""
<style>
    /* Global */
    .main { padding: 0 2rem; }
    section[data-testid="stSidebar"] { display: none; }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 1.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero p {
        font-size: 1.15rem;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    .hero-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: 600;
        font-size: 0.9rem;
        backdrop-filter: blur(10px);
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .card:hover {
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #f0f0f0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Section headings */
    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1a1a1a;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Price card */
    .price-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2.5rem;
        border-radius: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 50px rgba(17, 153, 142, 0.35);
        position: relative;
        overflow: hidden;
    }
    .price-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    @keyframes shimmer {
        0% { transform: translate(0, 0); }
        100% { transform: translate(20%, 20%); }
    }
    .price-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    .price-value {
        font-size: 4rem;
        font-weight: 900;
        margin: 0.5rem 0;
        line-height: 1;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .price-sub {
        font-size: 1.3rem;
        opacity: 0.95;
    }
    .price-range {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.3);
        font-size: 0.95rem;
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 0.75rem;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid #e9ecef;
        transition: all 0.2s;
    }
    .stat-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
    }
    .stat-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #667eea;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #6c757d;
        margin-top: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Input styling */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem !important;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        font-weight: 700;
        padding: 0.9rem;
        border-radius: 0.75rem;
        border: none;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        padding: 0.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #adb5bd;
        padding: 2rem 0;
        font-size: 0.85rem;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD MODEL
# ============================================================
@st.cache_resource
def _load():
    return load_artifacts()

try:
    model, metadata, mappings = _load()
    categories = get_category_values(mappings)
except Exception as e:
    st.error(f"⚠️ Model loading error: {e}")
    st.stop()

m = metadata["metrics"]


# ============================================================
# HERO
# ============================================================
st.markdown(f"""
<div class="hero">
    <h1>🏠 Smart House Price Predictor</h1>
    <p>AI-powered property price prediction for the Egyptian real estate market</p>
    <div class="hero-badges">
        <span class="hero-badge">📊 R² {m['r2']:.4f}</span>
        <span class="hero-badge">📉 MAPE {m['mape']:.2f}%</span>
        <span class="hero-badge">🎯 {metadata['features']['total']} Features</span>
        <span class="hero-badge">🤖 {metadata['model_name'].replace('_', ' ').title()}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# STATS ROW
# ============================================================
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{m["r2"]:.4f}</div><div class="stat-label">R² Score</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{m["mape"]:.2f}%</div><div class="stat-label">MAPE</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{m["mae"]/1000:,.0f}K</div><div class="stat-label">MAE (EGP)</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{metadata["features"]["total"]}</div><div class="stat-label">Features</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# INPUT FORM (3 columns)
# ============================================================
st.markdown('<div class="section-title">📝 Property Details</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><div class="card-title">📐 Size & Rooms</div>', unsafe_allow_html=True)
    area = st.slider("Area (m²)", 40, 500, 150, 5, key="area")
    bedrooms = st.selectbox("Bedrooms", ["studio","1","2","3","4","5","6"], index=3, key="bed")
    bathrooms = st.slider("Bathrooms", 1, 5, 2, key="bath")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📍 Location</div>', unsafe_allow_html=True)
    city = st.selectbox("City", categories["city"], key="city")
    town = st.selectbox("Town", categories["town"], key="town")
    district = st.selectbox("District", categories["district"], key="district")
    subdistrict = st.selectbox("Subdistrict", categories["subdistrict"], key="sub")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><div class="card-title">🏗️ Status & Features</div>', unsafe_allow_html=True)
    furnished = st.selectbox("Furnished", categories["furnished"], key="furn")
    completion_status = st.selectbox("Completion Status", categories["completion_status"], key="comp")
    c1, c2, c3 = st.columns(3)
    with c1: has_reception = st.checkbox("Reception", True, key="rec")
    with c2: has_living = st.checkbox("Living", True, key="liv")
    with c3: has_kitchen = st.checkbox("Kitchen", True, key="kit")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# DESCRIPTION
# ============================================================
st.markdown('<div class="section-title">📝 Property Description (Optional)</div>', unsafe_allow_html=True)
description = st.text_area(
    "Describe the property in Arabic or English",
    placeholder="e.g., شقة بحرية مفروشة سوبر لوكس فيو مفتوح / sea view furnished luxury apartment",
    height=80,
    label_visibility="collapsed",
    key="desc"
)


# ============================================================
# PREDICT BUTTON
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
predict_btn = st.button("🔮 Predict Property Price", type="primary", use_container_width=True)


# ============================================================
# BUILD FEATURES
# ============================================================
input_features = build_features(
    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
    city=city, town=town, district=district, subdistrict=subdistrict,
    furnished=furnished, completion_status=completion_status,
    has_reception=has_reception, has_living=has_living,
    has_kitchen=has_kitchen, description=description, mappings=mappings,
)


# ============================================================
# TABS
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯  Prediction",
    "🔍  AI Explanation",
    "🗺️  Price Map",
    "🎛️  What-If Analysis",
])


# ---------- Tab 1: Prediction ----------
with tab1:
    if predict_btn:
        errors = validate_input(area, bedrooms, bathrooms, city, town,
                                 district, subdistrict, furnished, completion_status)
        if errors:
            st.error("⚠️ " + " | ".join(errors))
        else:
            result = predict_with_confidence(model, input_features, m["mape"])
            price = result["price"]
            ppm = price / area

            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"""
                <div class="price-card">
                    <div class="price-label">Estimated Market Price</div>
                    <div class="price-value">{price/1_000_000:.2f}M</div>
                    <div class="price-sub">{price:,.0f} EGP</div>
                    <div class="price-range">
                        📊 Confidence Range: {format_price(result['lower_bound'])} — {format_price(result['upper_bound'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{ppm:,.0f}</div><div class="stat-label">Price per m² (EGP)</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                dist_avg = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
                diff = ppm - dist_avg
                diff_pct = (diff / dist_avg * 100) if dist_avg > 0 else 0
                color = "🟢" if diff >= 0 else "🔴"
                st.markdown(f'<div class="stat-card"><div class="stat-value">{dist_avg:,.0f}</div><div class="stat-label">District Avg (EGP/m²)</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f'<div class="stat-card"><div class="stat-value">{color} {diff_pct:+.1f}%</div><div class="stat-label">vs District Average</div></div>', unsafe_allow_html=True)

            # Gauge
            st.markdown("<br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=ppm,
                delta={"reference": dist_avg, "suffix": " EGP", "font": {"size": 14}},
                title={"text": "Price per m² vs District Average", "font": {"size": 16}},
                gauge={
                    "axis": {"range": [0, 80000], "tickwidth": 1},
                    "bar": {"color": "#667eea", "thickness": 0.75},
                    "steps": [
                        {"range": [0, 20000], "color": "#E8F5E9"},
                        {"range": [20000, 40000], "color": "#FFF9C4"},
                        {"range": [40000, 60000], "color": "#FFE0B2"},
                        {"range": [60000, 80000], "color": "#FFCDD2"},
                    ],
                    "threshold": {"line": {"color": "#e74c3c", "width": 3}, "value": dist_avg},
                },
                number={"suffix": " EGP/m²", "font": {"size": 32}},
            ))
            fig.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Fill in the property details above and click **Predict Property Price** to see the AI-powered estimate.")


# ---------- Tab 2: Explanation (SHAP) ----------
with tab2:
    st.markdown('<div class="section-title">🧠 Why This Price? (SHAP Explanation)</div>', unsafe_allow_html=True)
    st.caption("SHAP values show how each feature pushes the prediction up (green) or down (red).")

    @st.cache_resource
    def _shap_explainer(_model):
        return shap.TreeExplainer(_model.named_steps['model'])

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
            y=[feat_names[i].replace('num__','').replace('cat__','').replace('_', ' ').title() for i in idx],
            orientation='h',
            marker_color=colors,
            text=[f"{v:+.3f}" for v in sv_flat[idx]],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>SHAP: %{x:+.4f}<extra></extra>',
        ))
        fig.update_layout(
            title=f"Top {top_n} Feature Contributions",
            height=520,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis_title="SHAP Value (impact on log-price)",
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            plot_bgcolor='white',
        )
        st.plotly_chart(fig, use_container_width=True)

        pos = int(np.sum(sv_flat > 0))
        neg = int(np.sum(sv_flat < 0))
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{pos}</div><div class="stat-label">Features ↑ Price</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{neg}</div><div class="stat-label">Features ↓ Price</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{len(sv_flat)}</div><div class="stat-label">Total Features</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"SHAP error: {e}")


# ---------- Tab 3: Map ----------
with tab3:
    st.markdown('<div class="section-title">🗺️ Egypt Real Estate Price Map</div>', unsafe_allow_html=True)

    price_data = mappings["price_mappings"]["district_price_per_sqm"]
    city_centers = {
        "Cairo": (30.0444, 31.2357),
        "Giza": (30.0131, 31.2089),
        "Alexandria": (31.2001, 29.9187),
        "Mansoura": (31.0409, 31.3785),
        "Tanta": (30.7865, 31.0004),
    }

    m_map = folium.Map(location=[30.5, 31.2], zoom_start=7, tiles="cartodbpositron")

    for d_name, ppm_val in price_data.items():
        h = abs(hash(d_name))
        city_key = list(city_centers.keys())[h % 5]
        lat, lon = city_centers[city_key]
        lat += ((h // 7) % 60 - 30) / 500
        lon += ((h // 13) % 60 - 30) / 500

        color = '#43A047' if ppm_val < 25000 else '#FB8C00' if ppm_val < 40000 else '#E53935'
        radius = 8 + min(ppm_val / 5000, 12)

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.75,
            weight=2,
            popup=folium.Popup(f"<b>{d_name}</b><br>Avg: {ppm_val:,.0f} EGP/m²", max_width=200),
            tooltip=f"{d_name}: {ppm_val:,.0f} EGP/m²",
        ).add_to(m_map)

    st_folium(m_map, width=None, height=500, returned_objects=[])

    st.markdown('<div class="section-title">📊 District Ranking</div>', unsafe_allow_html=True)
    ppm_series = pd.Series(price_data).sort_values(ascending=True)
    fig2 = go.Figure(go.Bar(
        x=ppm_series.values,
        y=ppm_series.index,
        orientation='h',
        marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
        text=[f"{v:,.0f}" for v in ppm_series.values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} EGP/m²<extra></extra>',
    ))
    fig2.update_layout(
        title="Average Price per m² by District",
        height=650,
        margin=dict(l=20, r=60, t=60, b=20),
        xaxis_title="EGP per m²",
        plot_bgcolor='white',
    )
    st.plotly_chart(fig2, use_container_width=True)


# ---------- Tab 4: What-If ----------
with tab4:
    st.markdown('<div class="section-title">🎛️ What-If Scenario Analysis</div>', unsafe_allow_html=True)
    st.caption("Adjust parameters and instantly see how the predicted price changes.")

    base_price = predict_price(model, input_features)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{base_price/1_000_000:.2f}M</div><div class="stat-label">Base Price (Current Settings)</div><
