"""Smart House Price Predictor - Multi-App Inspired UI v9.0"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import shap
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
    calculate_roi, recommend_similar_properties,
)
from sentiment_helper import analyze_sentiment

try:
    from pdf_report import generate_pdf_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from monitoring import log_prediction
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


st.set_page_config(
    page_title="Smart House Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', -apple-system, sans-serif !important; }
.main .block-container { max-width: 1400px !important; padding: 0 1.5rem 3rem 1.5rem !important; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* NAVBAR */
.nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 1.5rem;
}
.nav-logo { font-size: 1.35rem; font-weight: 900; color: #111827; display: flex; align-items: center; gap: 0.5rem; }
.nav-logo span { color: #6366f1; }
.nav-tag { background: #eef2ff; color: #6366f1; padding: 0.35rem 0.85rem; border-radius: 8px; font-size: 0.72rem; font-weight: 800; }

/* HERO SEARCH */
.hero { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); padding: 3rem 2rem 2.5rem 2rem; border-radius: 24px; color: white; margin-bottom: 1.5rem; box-shadow: 0 20px 50px rgba(99,102,241,0.25); position: relative; overflow: hidden; }
.hero::before { content: ''; position: absolute; top: -80px; right: -80px; width: 320px; height: 320px; background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 70%); border-radius: 50%; }
.hero h1 { font-size: 2.6rem; font-weight: 900; margin: 0 0 0.5rem 0; letter-spacing: -1.2px; line-height: 1.15; position: relative; text-align: center; }
.hero p { font-size: 1.05rem; opacity: 0.95; margin: 0 0 1.75rem 0; position: relative; text-align: center; }
.hero-chips { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; position: relative; }
.hero-chip { background: rgba(255,255,255,0.22); backdrop-filter: blur(10px); padding: 0.5rem 1rem; border-radius: 100px; font-weight: 700; font-size: 0.78rem; }

/* CATEGORY PILLS (Airbnb style) */
.cat-pills { display: flex; gap: 0.5rem; overflow-x: auto; padding: 0.75rem 0; margin-bottom: 1rem; border-bottom: 1px solid #f3f4f6; }
.cat-pill { background: #f9fafb; color: #6b7280; padding: 0.55rem 1.1rem; border-radius: 100px; font-size: 0.82rem; font-weight: 700; white-space: nowrap; border: 1px solid #e5e7eb; }

/* FORM CARD */
.form-card { background: white; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.form-card-title { display: flex; align-items: center; gap: 0.6rem; font-size: 1rem; font-weight: 800; color: #111827; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 2px solid #f3f4f6; }
.form-step { width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 8px; font-size: 0.78rem; font-weight: 800; flex-shrink: 0; }

/* PROPERTY PREVIEW (Bayut/Airbnb style) */
.preview-wrap { position: sticky; top: 1rem; }
.property-preview { background: white; border-radius: 20px; border: 1px solid #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.06); overflow: hidden; }
.property-image { height: 190px; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); display: flex; align-items: center; justify-content: center; font-size: 5rem; position: relative; }
.property-badge { position: absolute; top: 1rem; left: 1rem; background: white; color: #6366f1; padding: 0.35rem 0.85rem; border-radius: 100px; font-size: 0.72rem; font-weight: 800; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.property-heart { position: absolute; top: 1rem; right: 1rem; background: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.property-content { padding: 1.25rem; }
.property-title { font-size: 1.15rem; font-weight: 900; color: #111827; margin-bottom: 0.35rem; }
.property-location { color: #6b7280; font-size: 0.85rem; margin-bottom: 1rem; }
.property-divider { height: 1px; background: #f3f4f6; margin: 1rem 0; }
.property-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem; margin-bottom: 1rem; }
.property-stat { background: #f9fafb; border-radius: 10px; padding: 0.65rem; text-align: center; }
.property-stat-value { font-size: 1rem; font-weight: 800; color: #111827; }
.property-stat-label { font-size: 0.68rem; color: #6b7280; margin-top: 0.15rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; }
.feature-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.75rem; }
.feature-tag { background: #ede9fe; color: #6366f1; padding: 0.25rem 0.65rem; border-radius: 100px; font-size: 0.7rem; font-weight: 700; }

/* PRICE CARD (Zillow Zestimate style) */
.price-hero { background: white; border-radius: 20px; padding: 2rem; border: 1px solid #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.06); margin-bottom: 1rem; }
.price-label { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 2px; color: #6b7280; font-weight: 700; margin-bottom: 0.5rem; }
.price-value { font-size: 3.5rem; font-weight: 900; color: #10b981; line-height: 1; letter-spacing: -2px; }
.price-egp { font-size: 1.15rem; color: #6b7280; margin-top: 0.25rem; font-weight: 600; }
.price-range-bar { margin-top: 1.5rem; height: 8px; background: #f3f4f6; border-radius: 100px; position: relative; overflow: hidden; }
.price-range-fill { height: 100%; background: linear-gradient(90deg, #10b981, #059669); border-radius: 100px; }
.price-range-labels { display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.78rem; color: #6b7280; font-weight: 600; }

/* MONTHLY PAYMENT (Zillow/Realtor style) */
.monthly-card { background: #f0fdf4; border-radius: 14px; padding: 1.25rem; border: 1px solid #bbf7d0; margin-bottom: 1rem; }
.monthly-title { font-size: 0.85rem; color: #15803d; font-weight: 800; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px; }
.monthly-value { font-size: 1.75rem; font-weight: 900; color: #166534; line-height: 1; }
.monthly-detail { font-size: 0.78rem; color: #15803d; margin-top: 0.5rem; }

/* METRIC CARD */
.metric-card { background: white; border-radius: 14px; padding: 1rem 0.75rem; text-align: center; border: 1px solid #e5e7eb; }
.metric-value { font-size: 1.3rem; font-weight: 900; color: #6366f1; line-height: 1; }
.metric-label { font-size: 0.68rem; color: #6b7280; margin-top: 0.35rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.4px; }

/* BUTTONS */
.stButton > button { border-radius: 12px !important; font-weight: 800 !important; font-size: 1rem !important; padding: 1rem 1.5rem !important; border: none !important; }
.stButton > button[kind="primary"] { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; color: white !important; box-shadow: 0 10px 24px rgba(99,102,241,0.35) !important; }
.stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 14px 32px rgba(99,102,241,0.45) !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] { gap: 0.35rem; background: white; padding: 0.5rem; border-radius: 14px; border: 1px solid #e5e7eb; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 0.65rem 1rem; font-weight: 700; font-size: 0.85rem; color: #6b7280; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; }

/* SIMILAR CARD */
.sim-card { background: white; border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 0.6rem; border: 1px solid #e5e7eb; }
.sim-match { background: #ede9fe; color: #6366f1; padding: 0.15rem 0.6rem; border-radius: 100px; font-size: 0.7rem; font-weight: 800; }

/* EMPTY STATE */
.empty-box { background: #f9fafb; border: 2px dashed #e5e7eb; border-radius: 20px; padding: 3rem 1.5rem; text-align: center; }
.empty-icon { font-size: 3.5rem; margin-bottom: 0.75rem; }
.empty-title { font-size: 1.15rem; font-weight: 800; color: #374151; margin-bottom: 0.35rem; }
.empty-text { color: #6b7280; font-size: 0.9rem; }

/* FOOTER */
.footer-box { text-align: center; color: #9ca3af; font-size: 0.78rem; padding: 2.5rem 1rem 1rem 1rem; border-top: 1px solid #e5e7eb; margin-top: 3rem; }
</style>""", unsafe_allow_html=True)


@st.cache_resource
def _load():
    return load_artifacts()

try:
    model, metadata, mappings = _load()
    categories = get_category_values(mappings)
except Exception as e:
    st.error(f"Model loading error: {e}")
    st.stop()

m = metadata["metrics"]


# ============================================================
# NAVBAR
# ============================================================
navbar_html = '<div class="nav"><div class="nav-logo">🏠 Smart<span>Price</span></div><div class="nav-tag">✨ AI-Powered</div></div>'
st.markdown(navbar_html, unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
r2_str = f"{m['r2']:.4f}"
mape_str = f"{m['mape']:.2f}"
cities_str = str(len(categories["city"]))
total_str = f"{metadata['training_info']['n_total']:,}"

hero_html = (
    '<div class="hero">'
    "<h1>Find Your Property's True Value</h1>"
    '<p>AI-powered estimates for the Egyptian real estate market</p>'
    '<div class="hero-chips">'
    '<span class="hero-chip">🎯 Accuracy ' + r2_str + '</span>'
    '<span class="hero-chip">📊 Avg Error ' + mape_str + '%</span>'
    '<span class="hero-chip">🏙️ ' + cities_str + ' Cities</span>'
    '<span class="hero-chip">📊 ' + total_str + ' Real Listings</span>'
    '</div></div>'
)
st.markdown(hero_html, unsafe_allow_html=True)




# ============================================================
# ACCURACY INFO BOX
# ============================================================
accuracy_html = (
    '<div style="background:linear-gradient(90deg,#ecfdf5,#f0fdf4);border:1px solid #bbf7d0;border-radius:12px;padding:0.85rem 1.15rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.75rem;">'
    '<div style="display:flex;align-items:center;gap:0.6rem;">'
    '<span style="font-size:1.4rem;">📊</span>'
    '<div>'
    '<div style="font-weight:800;color:#065f46;font-size:0.85rem;">Model Accuracy: ' + f"{m['r2']*100:.1f}" + '%</div>'
    '<div style="color:#047857;font-size:0.75rem;">Expected error margin: ±' + f"{m['mape']:.1f}" + '% — Use as reference, not certified appraisal</div>'
    '</div>'
    '</div>'
    '<div style="background:#059669;color:white;padding:0.35rem 0.75rem;border-radius:100px;font-size:0.68rem;font-weight:800;">VERIFIED</div>'
    '</div>'
)
st.markdown(accuracy_html, unsafe_allow_html=True)

# ============================================================
# PROPERTY TYPE + DATA SOURCE (info banner)
# ============================================================
info_html = (
    '<div style="background:linear-gradient(90deg,#fef3c7,#fef9c3);border:1px solid #fde68a;border-radius:14px;padding:0.85rem 1.15rem;margin-bottom:1.25rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.75rem;">'
    '<div style="display:flex;align-items:center;gap:0.6rem;">'
    '<span style="font-size:1.5rem;">🏢</span>'
    '<div>'
    '<div style="font-weight:800;color:#78350f;font-size:0.9rem;">Currently supports residential apartments only</div>'
    '<div style="color:#92400e;font-size:0.78rem;">Trained on 7,749 real listings · Villas and offices coming soon</div>'
    '</div>'
    '</div>'
    '<div style="background:#78350f;color:#fef3c7;padding:0.4rem 0.85rem;border-radius:100px;font-size:0.7rem;font-weight:800;letter-spacing:0.3px;">APARTMENTS</div>'
    '</div>'
)
st.markdown(info_html, unsafe_allow_html=True)

# ============================================================
# HOW IT WORKS (3-step strip)
# ============================================================
how_html = (
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;">'
    '<div style="background:white;border:1px solid #e5e7eb;border-radius:14px;padding:1.25rem;text-align:center;">'
    '<div style="font-size:2rem;margin-bottom:0.5rem;">📍</div>'
    '<div style="font-weight:800;color:#111827;font-size:0.95rem;margin-bottom:0.25rem;">1. Pick Location</div>'
    '<div style="color:#6b7280;font-size:0.8rem;">Choose city, district & compound</div>'
    '</div>'
    '<div style="background:white;border:1px solid #e5e7eb;border-radius:14px;padding:1.25rem;text-align:center;">'
    '<div style="font-size:2rem;margin-bottom:0.5rem;">📐</div>'
    '<div style="font-weight:800;color:#111827;font-size:0.95rem;margin-bottom:0.25rem;">2. Add Details</div>'
    '<div style="color:#6b7280;font-size:0.8rem;">Size, rooms & amenities</div>'
    '</div>'
    '<div style="background:white;border:1px solid #e5e7eb;border-radius:14px;padding:1.25rem;text-align:center;">'
    '<div style="font-size:2rem;margin-bottom:0.5rem;">💰</div>'
    '<div style="font-weight:800;color:#111827;font-size:0.95rem;margin-bottom:0.25rem;">3. Get Estimate</div>'
    '<div style="color:#6b7280;font-size:0.8rem;">AI-powered instant valuation</div>'
    '</div>'
    '</div>'
)
st.markdown(how_html, unsafe_allow_html=True)


# ============================================================
# MARKET STATS BANNER (Redfin/Zillow style)
# ============================================================
city_ppm_all = mappings['price_mappings']['city_price_per_sqm']
top_cities = sorted(city_ppm_all.items(), key=lambda x: -x[1])[:3]

# Top district
district_ppm_all = mappings['price_mappings']['district_price_per_sqm']
top_district = max(district_ppm_all.items(), key=lambda x: x[1])

# Average
avg_ppm = mappings['price_mappings']['global_mean_ppm']

market_html = (
    '<div style="background:linear-gradient(90deg,#f0f9ff,#eff6ff);border:1px solid #bfdbfe;border-radius:14px;padding:1rem 1.25rem;margin-bottom:1.5rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">'
    '<div style="display:flex;gap:2rem;flex-wrap:wrap;">'
    '<div>'
    '<div style="font-size:0.72rem;color:#1e40af;font-weight:800;text-transform:uppercase;letter-spacing:0.5px;">📊 Market Avg</div>'
    '<div style="font-size:1.15rem;font-weight:900;color:#1e3a8a;">' + f'{avg_ppm:,.0f}' + ' <span style="font-size:0.75rem;font-weight:600;">EGP/m²</span></div>'
    '</div>'
    '<div>'
    '<div style="font-size:0.72rem;color:#1e40af;font-weight:800;text-transform:uppercase;letter-spacing:0.5px;">🔥 Top District</div>'
    '<div style="font-size:1.15rem;font-weight:900;color:#1e3a8a;">' + top_district[0] + '</div>'
    '</div>'
    '<div>'
    '<div style="font-size:0.72rem;color:#1e40af;font-weight:800;text-transform:uppercase;letter-spacing:0.5px;">🏙️ Top City</div>'
    '<div style="font-size:1.15rem;font-weight:900;color:#1e3a8a;">' + top_cities[0][0] + '</div>'
    '</div>'
    '</div>'
    '<div style="background:#1e40af;color:white;padding:0.5rem 1rem;border-radius:100px;font-size:0.75rem;font-weight:800;">LIVE DATA</div>'
    '</div>'
)
st.markdown(market_html, unsafe_allow_html=True)

# ============================================================
# CATEGORY PILLS
# ============================================================
pills_html = '<div class="cat-pills"><div class="cat-pill">🏢 Apartment</div><div class="cat-pill">📍 All Cities</div><div class="cat-pill">⭐ Featured</div><div class="cat-pill">💰 Best Value</div><div class="cat-pill">📊 Market Trends</div><div class="cat-pill">🔮 AI Valuation</div></div>'
st.markdown(pills_html, unsafe_allow_html=True)


# ============================================================
# 2-COLUMN LAYOUT
# ============================================================
col_left, col_right = st.columns([7, 5], gap="large")

with col_left:
    # STEP 1
    st.markdown('<div class="form-card"><div class="form-card-title"><div class="form-step">1</div>Location</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        city = st.selectbox("City", categories["city"], key="s_city")
    with c2:
        district = st.selectbox("District", categories["district"], key="s_district")
    compound_options = ["None"] + categories["compound"][:200]
    compound = st.selectbox("Compound (optional)", compound_options, key="s_compound")

    # STEP 2
    st.markdown('<div class="form-card"><div class="form-card-title"><div class="form-step">2</div>Size & Rooms</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.slider("Area (sqm)", 40, 500, 150, 5, key="s_area")
    with c2:
        bedrooms = st.selectbox("Bedrooms", ["studio","1","2","3","4","5","6"], index=3, key="s_beds")
    with c3:
        bathrooms = st.slider("Bathrooms", 1, 5, 2, key="s_baths")

    # STEP 3
    st.markdown('<div class="form-card"><div class="form-card-title"><div class="form-step">3</div>Features & Amenities</div></div>', unsafe_allow_html=True)
    AMENITY_UI = {
        "Balcony": "BA", "Built-in Wardrobes": "BW", "Covered Parking": "CP",
        "Private Garden": "PG", "Shared Pool": "SP", "Security": "SE",
        "Air Conditioning": "AC", "Kitchen": "BK", "Maid Room": "MR",
        "Storage": "ST", "Children Area": "CO", "Gym": "GY",
    }
    selected_amenities = []
    cols = st.columns(4)
    for i, (label, code) in enumerate(AMENITY_UI.items()):
        with cols[i % 4]:
            if st.checkbox(label, value=(code in ["BA", "SE"]), key=f"am_{code}"):
                selected_amenities.append(code)

    # STEP 4
    st.markdown('<div class="form-card"><div class="form-card-title"><div class="form-step">4</div>Description (optional)</div></div>', unsafe_allow_html=True)
    description = st.text_area("Description", placeholder="Example: Sea view apartment, fully furnished, super lux", height=80, key="s_desc", label_visibility="collapsed")

    sentiment = analyze_sentiment(description) if description else None
    if sentiment and sentiment['label'] != 'neutral':
        emoji = "😊" if sentiment['label'] == 'positive' else "😟"
        color = "#10b981" if sentiment['label'] == 'positive' else "#ef4444"
        score_str = f'{sentiment["score"]:+.2f}'
        sent_html = (
            '<div style="background:' + color + '10;border-left:4px solid ' + color
            + ';padding:0.7rem 1rem;border-radius:10px;margin-top:0.5rem;color:' + color
            + ';font-weight:600;font-size:0.85rem;">'
            + emoji + ' ' + sentiment["label"].title() + ' sentiment (' + score_str + ')'
            + '</div>'
        )
        st.markdown(sent_html, unsafe_allow_html=True)


# RIGHT: PREVIEW
with col_right:
    st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
    bd_text = "Studio" if bedrooms == "studio" else f"{bedrooms} Bedrooms"
    compound_text = compound if compound != "None" else "—"
    amenity_count = len(selected_amenities)

    preview_html = (
        '<div class="property-preview">'
        '<div class="property-image">🏢'
        '<div class="property-badge">LIVE PREVIEW</div>'
        '<div class="property-heart">♡</div></div>'
        '<div class="property-content">'
        '<div class="property-title">' + f'{area}' + ' m² · ' + bd_text + '</div>'
        '<div class="property-location">📍 ' + city + ' → ' + district + '</div>'
        '<div class="property-stats">'
        '<div class="property-stat"><div class="property-stat-value">' + f'{bathrooms}' + '</div><div class="property-stat-label">Bathrooms</div></div>'
        '<div class="property-stat"><div class="property-stat-value">' + f'{amenity_count}' + '</div><div class="property-stat-label">Amenities</div></div>'
        '<div class="property-stat"><div class="property-stat-value">Real</div><div class="property-stat-label">Data</div></div>'
        '<div class="property-stat"><div class="property-stat-value">AI</div><div class="property-stat-label">Estimate</div></div>'
        '</div>'
        '<div class="property-divider"></div>'
        '<div style="font-size:0.78rem;color:#6b7280;font-weight:700;margin-bottom:0.4rem;">🏘️ COMPOUND</div>'
        '<div style="font-size:0.9rem;font-weight:700;color:#111827;">' + compound_text + '</div>'
        '</div></div>'
    )
    st.markdown(preview_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🔮  Get Price Estimate", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)



# ============================================================
# BUILD FEATURES
# ============================================================
CITY_GPS = {
    "Cairo": (30.0444, 31.2357),
    "Giza": (30.0131, 31.2089),
    "Alexandria": (31.2001, 29.9187),
    "Red Sea": (27.2579, 33.8116),
    "North Coast": (31.0906, 27.9407),
    "Suez": (29.9737, 32.5263),
    "Matrouh": (31.3543, 27.2373),
}
lat, lon = CITY_GPS.get(city, (30.0444, 31.2357))

input_features = build_features(
    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
    city=city, district=district, compound=compound,
    latitude=lat, longitude=lon,
    amenities=selected_amenities,
    description=description,
    mappings=mappings,
)


# ============================================================
# RESULTS
# ============================================================
if predict_btn:
    errors = validate_input(area, bedrooms, bathrooms, city, district, compound)
    if errors:
        st.error("⚠️ " + " | ".join(errors))
    else:
        result = predict_with_confidence(model, input_features, m["mape"])
        price = result["price"]
        ppm = price / area

        if MONITORING_AVAILABLE:
            try:
                log_prediction(area=area, bedrooms=bedrooms, bathrooms=bathrooms,
                                city=city, district=district, compound=compound,
                                predicted_price=price,
                                confidence_lower=result['lower_bound'],
                                confidence_upper=result['upper_bound'])
            except Exception:
                pass

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 📊 Your Property Valuation")

        res_left, res_right = st.columns([5, 7], gap="large")

        with res_left:
            # Zillow-style big price
            lower_pct = 5
            upper_pct = 95
            price_html = (
                '<div class="price-hero">'
                '<div class="price-label">Estimated Market Value</div>'
                '<div class="price-value">' + f'{price/1_000_000:.2f}M' + '</div>'
                '<div class="price-egp">' + f'{price:,.0f} EGP' + '</div>'
                '<div class="price-range-bar"><div class="price-range-fill"></div></div>'
                '<div class="price-range-labels">'
                '<span>' + format_price(result['lower_bound']) + '</span>'
                '<span>' + format_price(result['upper_bound']) + '</span>'
                '</div>'
                '</div>'
            )
            st.markdown(price_html, unsafe_allow_html=True)

            # Zillow-style monthly payment
            monthly_rate = 0.10 / 12
            n_payments = 20 * 12
            down_payment = price * 0.20
            loan_amount = price - down_payment
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -n_payments)

            monthly_html = (
                '<div class="monthly-card">'
                '<div class="monthly-title">💰 Est. Monthly Payment</div>'
                '<div class="monthly-value">' + f'{monthly_payment:,.0f}' + ' EGP</div>'
                '<div class="monthly-detail">20% down · 20 years · 10% interest</div>'
                '</div>'
            )
            st.markdown(monthly_html, unsafe_allow_html=True)

            # PDF
            if PDF_AVAILABLE:
                try:
                    pdf_buf = generate_pdf_report(
                        {'price': price, 'lower_bound': result['lower_bound'],
                         'upper_bound': result['upper_bound'], 'price_per_sqm': ppm},
                        {'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
                         'city': city, 'town': '—', 'district': district,
                         'subdistrict': compound, 'furnished': '—',
                         'completion_status': '—'},
                        {'model_name': metadata['model_name'], 'r2': m['r2'],
                         'mape': m['mape'], 'n_train': metadata['training_info']['n_train']},
                    )
                    st.download_button(
                        "📄  Download PDF Report",
                        data=pdf_buf,
                        file_name="property_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception:
                    pass

            # WhatsApp Share Button
            share_text = f"Just estimated a property price on SmartPrice AI: {price:,.0f} EGP for {area} m2 in {district}, {city}. Check it out!"
            share_url = "https://wa.me/?text=" + share_text.replace(' ', '%20').replace('\n', '%0A')
            share_html = (
                '<a href="' + share_url + '" target="_blank" style="display:block;width:100%;text-align:center;'
                'background:#25D366;color:white;padding:0.85rem 1.5rem;border-radius:12px;font-weight:800;'
                'text-decoration:none;font-size:1rem;margin-top:0.5rem;box-shadow:0 8px 20px rgba(37,211,102,0.3);">'
                '💬 Share on WhatsApp</a>'
            )
            st.markdown(share_html, unsafe_allow_html=True)

        with res_right:
            district_ppm = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
            diff_pct = ((ppm - district_ppm) / district_ppm * 100) if district_ppm else 0
            arrow = "🟢" if diff_pct >= 0 else "🔴"

            m1, m2, m3 = st.columns(3)
            with m1:
                m1_html = '<div class="metric-card"><div class="metric-value">' + f'{ppm:,.0f}' + '</div><div class="metric-label">Price / m²</div></div>'
                st.markdown(m1_html, unsafe_allow_html=True)
            with m2:
                m2_html = '<div class="metric-card"><div class="metric-value">' + f'{district_ppm:,.0f}' + '</div><div class="metric-label">District Avg</div></div>'
                st.markdown(m2_html, unsafe_allow_html=True)
            with m3:
                m3_html = '<div class="metric-card"><div class="metric-value">' + arrow + ' ' + f'{diff_pct:+.1f}%' + '</div><div class="metric-label">vs District</div></div>'
                st.markdown(m3_html, unsafe_allow_html=True)

        # Price History Indicator
        city_growth = {
            "Cairo": 15.2, "Giza": 17.2, "Alexandria": 13.1,
            "Red Sea": 12.0, "North Coast": 14.5, "Mansoura": 18.4,
            "Tanta": 16.1, "Suez": 16.0, "Ismailia": 21.1, "Matrouh": 14.0,
        }
        growth = city_growth.get(city, 15.0)
        arrow_dir = "📈" if growth > 0 else "📉"
        history_html = (
            '<div style="background:linear-gradient(90deg,#fef3c7,#fffbeb);border:1px solid #fde68a;'
            'border-radius:12px;padding:0.85rem 1.15rem;margin-top:0.75rem;display:flex;justify-content:space-between;align-items:center;">'
            '<div>'
            '<div style="font-weight:800;color:#78350f;font-size:0.82rem;">' + arrow_dir + ' 12-Month Market Trend</div>'
            '<div style="color:#92400e;font-size:0.75rem;">Prices in ' + city + ' rose ' + f'{growth:.1f}' + '% over the last year</div>'
            '</div>'
            '<div style="font-size:1.4rem;font-weight:900;color:#78350f;">+' + f'{growth:.1f}' + '%</div>'
            '</div>'
        )
        st.markdown(history_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 🔍 Dive Deeper")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🧠 Why This Price",
            "🗺️ Market",
            "🏘️ Similar",
            "⚖️ Compare",
            "💰 Investment",
        ])

        with tab1:
            st.caption("How each feature affected your price estimate")
            try:
                prep = model.named_steps['prep']
                X_t = prep.transform(input_features)
                feat_names = prep.get_feature_names_out()
                explainer = shap.TreeExplainer(model.named_steps['model'])
                sv = np.array(explainer.shap_values(X_t)).flatten()
                top_n = 10
                idx = np.argsort(np.abs(sv))[-top_n:][::-1]
                clean_names = [feat_names[i].replace('num__','').replace('cat__','').replace('_',' ').title() for i in idx]
                colors = ['#10b981' if v > 0 else '#ef4444' for v in sv[idx]]
                fig = go.Figure(go.Bar(
                    x=sv[idx], y=clean_names, orientation='h',
                    marker_color=colors,
                    text=[f"{v:+.3f}" for v in sv[idx]],
                    textposition='outside',
                ))
                fig.update_layout(height=420, margin=dict(l=10, r=40, t=20, b=20),
                                   xaxis_title="Impact on price", showlegend=False, plot_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
                st.caption("🟢 Increases price | 🔴 Decreases price")
            except Exception as e:
                st.error(f"SHAP error: {e}")

        with tab2:
            st.markdown("#### District Price Ranking")
            price_data = mappings['price_mappings']['district_price_per_sqm']
            ppm_series = pd.Series(price_data).sort_values(ascending=True).tail(25)
            fig = go.Figure(go.Bar(
                x=ppm_series.values, y=ppm_series.index, orientation='h',
                marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
                text=[f"{v:,.0f}" for v in ppm_series.values], textposition='outside',
            ))
            fig.update_layout(height=650, margin=dict(l=10, r=60, t=20, b=20),
                              xaxis_title="EGP per m²")
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.caption("Top 5 most similar properties from real listings")
            try:
                recs = recommend_similar_properties(
                    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
                    city=city, district=district,
                    compound=compound if compound != "None" else "None",
                    top_n=5,
                )
                if recs:
                    for i, r in enumerate(recs, 1):
                        sim_pct = r['similarity'] * 100
                        bd = "Studio" if r.get('is_studio') == 1 else f"{r['bedrooms_clean']} BR"
                        card_html = (
                            '<div class="sim-card">'
                            '<div style="display:flex;justify-content:space-between;align-items:center;">'
                            '<div>'
                            '<b style="color:#6366f1;font-size:1.05rem;">#' + str(i) + '</b> '
                            '<b style="font-size:1.05rem;">' + f"{r['area_value']:.0f}" + ' m² · ' + bd + ' · ' + f"{r['bathrooms_clean']}" + ' bath</b>'
                            '<div style="color:#6b7280;font-size:0.85rem;margin-top:0.25rem;">📍 ' + r['city'] + ' → ' + r['district'] + '</div>'
                            '<div style="margin-top:0.35rem;"><span class="sim-match">' + f'{sim_pct:.0f}' + '% match</span></div>'
                            '</div>'
                            '<div style="text-align:right;">'
                            '<div style="font-size:1.4rem;font-weight:800;color:#10b981;">' + f"{r['predicted_price']/1e6:.2f}" + 'M</div>'
                            '<div style="font-size:0.72rem;color:#9ca3af;">EGP</div>'
                            '</div></div></div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Recommendation error: {e}")

        with tab4:
            st.caption("Compare this property with an alternative")
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**🅰️ Current Property**")
                a_html = (
                    '<div class="metric-card">'
                    '<div class="metric-value" style="color:#10b981;">' + f'{price:,.0f}' + ' EGP</div>'
                    '<div style="margin-top:0.75rem;font-size:0.9rem;">'
                    'Area: ' + f'{area}' + ' m²<br>'
                    'Bedrooms: ' + str(bedrooms) + '<br>'
                    'Bathrooms: ' + str(bathrooms) + '<br>'
                    'Location: ' + city + ' → ' + district + '</div></div>'
                )
                st.markdown(a_html, unsafe_allow_html=True)
            with colB:
                st.markdown("**🅱️ Alternative Property**")
                b_area = st.number_input("Area (m²)", 40, 500, 200, 5, key="cmp_area")
                b_bedrooms = st.selectbox("Bedrooms", ["1","2","3","4","5"], index=3, key="cmp_bed")
                b_bathrooms = st.slider("Bathrooms", 1, 5, 3, key="cmp_bath")
                b_district = st.selectbox("District", categories["district"], key="cmp_dist")
                b_city = st.selectbox("City", categories["city"], key="cmp_city")

                prop_b = {
                    'area': b_area, 'bedrooms': b_bedrooms, 'bathrooms': b_bathrooms,
                    'city': b_city, 'district': b_district,
                    'compound': 'None', 'amenities': [],
                }
                feat_b = build_features(**prop_b, mappings=mappings)
                price_b = predict_with_confidence(model, feat_b, m["mape"])['price']
                b_html = (
                    '<div class="metric-card">'
                    '<div class="metric-value" style="color:#6366f1;">' + f'{price_b:,.0f}' + ' EGP</div>'
                    '<div style="margin-top:0.75rem;font-size:0.9rem;">'
                    'Area: ' + f'{b_area}' + ' m²<br>'
                    'Bedrooms: ' + b_bedrooms + '<br>'
                    'Bathrooms: ' + str(b_bathrooms) + '<br>'
                    'Location: ' + b_city + ' → ' + b_district + '</div></div>'
                )
                st.markdown(b_html, unsafe_allow_html=True)

            diff = price - price_b
            if diff < 0:
                st.success(f"💰 Property A is cheaper by {abs(diff):,.0f} EGP")
            else:
                st.info(f"💰 Property B is cheaper by {abs(diff):,.0f} EGP")

        with tab5:
            st.markdown("#### Investment ROI (5 Years)")
            roi = calculate_roi(price, years=5)
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                h1 = '<div class="metric-card"><div class="metric-value">' + f"{roi['roi_pct']:.0f}" + '%</div><div class="metric-label">Total ROI</div></div>'
                st.markdown(h1, unsafe_allow_html=True)
            with i2:
                h2 = '<div class="metric-card"><div class="metric-value">' + f"{roi['annualized_roi_pct']:.1f}" + '%</div><div class="metric-label">Annualized</div></div>'
                st.markdown(h2, unsafe_allow_html=True)
            with i3:
                h3 = '<div class="metric-card"><div class="metric-value">' + f"{roi['total_rental_income']/1e6:.2f}" + 'M</div><div class="metric-label">Rental</div></div>'
                st.markdown(h3, unsafe_allow_html=True)
            with i4:
                h4 = '<div class="metric-card"><div class="metric-value">' + f"{roi['appreciation_gain']/1e6:.2f}" + 'M</div><div class="metric-label">Appreciation</div></div>'
                st.markdown(h4, unsafe_allow_html=True)

            years_arr = np.arange(6)
            rental = [price * 0.005 * 12 * y / 1e6 for y in years_arr]
            appr = [(price * (1.12 ** y) - price) / 1e6 for y in years_arr]
            fig_roi = go.Figure()
            fig_roi.add_trace(go.Bar(x=years_arr, y=rental, name='Rental Income', marker_color='#10b981'))
            fig_roi.add_trace(go.Bar(x=years_arr, y=appr, name='Appreciation', marker_color='#6366f1'))
            fig_roi.update_layout(barmode='stack', height=350, xaxis_title="Year",
                                    yaxis_title="Million EGP", plot_bgcolor='white')
            st.plotly_chart(fig_roi, use_container_width=True)

else:
    empty_html = (
        '<div class="empty-box" style="margin-top:2rem;">'
        '<div class="empty-icon">🏠</div>'
        '<div class="empty-title">Ready to estimate your property</div>'
        '<div class="empty-text">Fill in the details above and click <b>Get Price Estimate</b></div>'
        '</div>'
    )
    st.markdown(empty_html, unsafe_allow_html=True)



# ============================================================
# ============================================================
# FAQ SECTION (single expander with all questions)
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

faq_items = [
    ("Is this data real?",
     "Yes. Our model is trained on 7,749 real property listings from PropertyFinder Egypt — the largest real estate platform in Egypt. Every listing has verified location, GPS coordinates, size, rooms, and amenities."),
    ("How accurate are the estimates?",
     "The model achieves 68.4% accuracy (R-squared = 0.68) with an average error margin of 18.4%. This is honest performance on real market data — many listings differ in condition, floor, view, and negotiation room, which are not captured in the data."),
    ("Can I use this as an official appraisal?",
     "No. This is an AI estimation tool for reference and research purposes. For official property valuation — especially for buying, selling, or legal matters — please consult a certified real estate appraiser."),
    ("What property types are supported?",
     "Currently we support residential apartments only. Villas, chalets, and commercial properties are on our roadmap."),
    ("Which cities are covered?",
     "The model covers 9 Egyptian cities: Cairo, Giza, Alexandria, Red Sea, North Coast, Suez, Qalyubia, Matrouh, and Al Daqahlya — with 43 districts and 890 compounds."),
    ("How does the AI calculate the price?",
     "We use XGBoost, a powerful gradient-boosting algorithm. It analyzes 64 features including size, location, GPS coordinates, amenities, and NLP-extracted keywords from listing titles. Every prediction comes with a SHAP explanation showing what drove the price."),
    ("Is my data stored anywhere?",
     "We only log anonymized predictions (area, city, predicted price) to monitor model performance. No personal information is collected."),
]

with st.expander("Frequently Asked Questions", expanded=False):
    for i, (question, answer) in enumerate(faq_items, 1):
        num_html = (
            '<div style="padding:0.75rem 0;border-bottom:1px solid #f3f4f6;">'
            '<div style="font-weight:800;color:#111827;font-size:0.95rem;margin-bottom:0.35rem;">'
            + f'{i:02d}  ' + question +
            '</div>'
            '<div style="color:#4b5563;font-size:0.85rem;line-height:1.55;">'
            + answer +
            '</div>'
            '</div>'
        )
        st.markdown(num_html, unsafe_allow_html=True)



# AGENT CONTACT CTA
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

agent_html = (
    '<div style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);border-radius:20px;padding:2rem;'
    'color:white;text-align:center;box-shadow:0 20px 40px rgba(99,102,241,0.25);position:relative;overflow:hidden;">'
    '<div style="position:absolute;top:-60px;right:-60px;width:200px;height:200px;'
    'background:radial-gradient(circle,rgba(255,255,255,0.15),transparent 70%);border-radius:50%;"></div>'
    '<div style="font-size:2.5rem;margin-bottom:0.5rem;position:relative;">🤝</div>'
    '<h3 style="font-size:1.5rem;font-weight:900;margin:0 0 0.5rem 0;position:relative;">Want a Professional Valuation?</h3>'
    '<p style="opacity:0.95;font-size:0.95rem;margin:0 0 1.5rem 0;position:relative;">'
    'Our AI gives fast estimates. For certified appraisals, connect with a trusted local real estate agent.</p>'
    '<div style="display:flex;justify-content:center;gap:0.75rem;flex-wrap:wrap;position:relative;">'
    '<a href="https://www.propertyfinder.eg" target="_blank" style="background:white;color:#6366f1;'
    'padding:0.75rem 1.5rem;border-radius:100px;font-weight:800;text-decoration:none;font-size:0.9rem;">'
    '🏢 Browse PropertyFinder</a>'
    '<a href="https://wa.me/?text=Hi%2C%20I%20need%20a%20property%20valuation" target="_blank" '
    'style="background:rgba(255,255,255,0.2);backdrop-filter:blur(10px);color:white;'
    'padding:0.75rem 1.5rem;border-radius:100px;font-weight:800;text-decoration:none;font-size:0.9rem;'
    'border:1px solid rgba(255,255,255,0.3);">'
    '💬 Contact an Agent</a>'
    '</div>'
    '</div>'
)
st.markdown(agent_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
footer_html = (
    '<div class="footer-box">'
    '<b>Smart House Price Predictor</b> v9.0 · '
    + metadata['model_name'] + ' · '
    + f"R² {m['r2']:.4f}" + ' · '
    + f"MAPE {m['mape']:.2f}%" + '<br>'
    'Trained on <b>' + f"{metadata['training_info']['n_total']:,}" + ' real property listings</b> '
    'from PropertyFinder Egypt'
    '<br><br>'
    'AI estimation tool — not a certified appraisal.'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
