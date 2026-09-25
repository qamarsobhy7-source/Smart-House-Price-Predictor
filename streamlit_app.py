"""Smart House Price Predictor - v10.0 (Mobile-First Layout)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import shap
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import joblib

# Load time series forecasts
@st.cache_resource
def _load_forecasts():
    """Load time series forecasts (cached)."""
    try:
        from pathlib import Path
        ts_path = Path(__file__).resolve().parent / "models" / "time_series_forecasts.joblib"
        if ts_path.exists():
            return joblib.load(ts_path)
    except Exception:
        pass
    return None


# Load map data
@st.cache_resource
def _load_map_data():
    """Load map data (cached)."""
    try:
        from pathlib import Path
        map_path = Path(__file__).resolve().parent / "data" / "real_data" / "map_data.csv"
        if map_path.exists():
            return pd.read_csv(map_path)
    except Exception:
        pass
    return None

from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
    calculate_roi, recommend_similar_properties,
)
# Use AraBERT for Arabic sentiment analysis
try:
    from arabert_helper import analyze_sentiment, get_sentiment_emoji
    ARABERT_AVAILABLE = True
except ImportError:
    from sentiment_helper import analyze_sentiment
    ARABERT_AVAILABLE = False
    def get_sentiment_emoji(label):
        return {"positive": "😊", "negative": "😟", "neutral": "😐"}.get(label, "😐")

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
.main .block-container { max-width: 1200px !important; padding: 1rem 1rem 3rem 1rem !important; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* NAVBAR */
.nav { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 1.5rem; }
.nav-logo { font-size: 1.2rem; font-weight: 900; color: #111827; }
.nav-logo span { color: #6366f1; }
.nav-tag { background: #eef2ff; color: #6366f1; padding: 0.3rem 0.75rem; border-radius: 8px; font-size: 0.7rem; font-weight: 800; }

/* HERO */
.hero { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); padding: 2rem 1.5rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 15px 40px rgba(99,102,241,0.25); }
.hero h1 { font-size: 1.9rem; font-weight: 900; margin: 0 0 0.5rem 0; letter-spacing: -0.5px; line-height: 1.2; }
.hero p { font-size: 0.95rem; opacity: 0.95; margin: 0 0 1rem 0; }
.hero-badges { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; }
.hero-badge { background: rgba(255,255,255,0.22); padding: 0.4rem 0.85rem; border-radius: 100px; font-weight: 700; font-size: 0.72rem; }

/* FORM CARD */
.form-card { background: white; border-radius: 14px; padding: 1.15rem; margin-bottom: 0.75rem; border: 1px solid #e5e7eb; }
.form-card-title { display: flex; align-items: center; gap: 0.5rem; font-size: 0.95rem; font-weight: 800; color: #111827; margin-bottom: 0.85rem; padding-bottom: 0.65rem; border-bottom: 2px solid #f3f4f6; }
.form-step { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 7px; font-size: 0.72rem; font-weight: 800; flex-shrink: 0; }

/* PROPERTY PREVIEW */
.property-preview { background: white; border-radius: 16px; border: 1px solid #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.06); overflow: hidden; }
.property-image { height: 160px; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); display: flex; align-items: center; justify-content: center; font-size: 4rem; position: relative; }
.property-badge { position: absolute; top: 0.85rem; left: 0.85rem; background: white; color: #6366f1; padding: 0.3rem 0.7rem; border-radius: 100px; font-size: 0.65rem; font-weight: 800; }
.property-heart { position: absolute; top: 0.85rem; right: 0.85rem; background: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; }
.property-content { padding: 1rem; }
.property-title { font-size: 1.05rem; font-weight: 900; color: #111827; margin-bottom: 0.3rem; }
.property-location { color: #6b7280; font-size: 0.82rem; margin-bottom: 0.85rem; }
.property-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.property-stat { background: #f9fafb; border-radius: 8px; padding: 0.55rem; text-align: center; }
.property-stat-value { font-size: 0.95rem; font-weight: 800; color: #111827; }
.property-stat-label { font-size: 0.62rem; color: #6b7280; margin-top: 0.15rem; font-weight: 700; text-transform: uppercase; }

/* PRICE CARD */
.price-hero { background: white; border-radius: 16px; padding: 1.5rem; border: 1px solid #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.06); margin-bottom: 1rem; }
.price-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 2px; color: #6b7280; font-weight: 700; margin-bottom: 0.4rem; }
.price-value { font-size: 2.75rem; font-weight: 900; color: #10b981; line-height: 1; letter-spacing: -1.5px; }
.price-egp { font-size: 1rem; color: #6b7280; margin-top: 0.2rem; font-weight: 600; }
.price-range-bar { margin-top: 1rem; height: 7px; background: #f3f4f6; border-radius: 100px; overflow: hidden; }
.price-range-fill { height: 100%; background: linear-gradient(90deg, #10b981, #059669); border-radius: 100px; }
.price-range-labels { display: flex; justify-content: space-between; margin-top: 0.4rem; font-size: 0.72rem; color: #6b7280; font-weight: 600; }

/* MONTHLY */
.monthly-card { background: #f0fdf4; border-radius: 12px; padding: 1rem; border: 1px solid #bbf7d0; margin-bottom: 0.85rem; }
.monthly-title { font-size: 0.75rem; color: #15803d; font-weight: 800; margin-bottom: 0.35rem; text-transform: uppercase; }
.monthly-value { font-size: 1.5rem; font-weight: 900; color: #166534; line-height: 1; }
.monthly-detail { font-size: 0.72rem; color: #15803d; margin-top: 0.35rem; }

/* METRIC CARD */
.metric-card { background: white; border-radius: 12px; padding: 0.85rem 0.6rem; text-align: center; border: 1px solid #e5e7eb; }
.metric-value { font-size: 1.15rem; font-weight: 900; color: #6366f1; line-height: 1; }
.metric-label { font-size: 0.62rem; color: #6b7280; margin-top: 0.3rem; font-weight: 800; text-transform: uppercase; }

/* BUTTONS */
.stButton > button { border-radius: 12px !important; font-weight: 800 !important; font-size: 1rem !important; padding: 0.9rem 1.5rem !important; border: none !important; }
.stButton > button[kind="primary"] { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; color: white !important; box-shadow: 0 10px 24px rgba(99,102,241,0.35) !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] { gap: 0.3rem; background: white; padding: 0.4rem; border-radius: 12px; border: 1px solid #e5e7eb; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 0.55rem 0.85rem; font-weight: 700; font-size: 0.8rem; color: #6b7280; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; }

/* SIMILAR CARD */
.sim-card { background: white; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; border: 1px solid #e5e7eb; }
.sim-match { background: #ede9fe; color: #6366f1; padding: 0.15rem 0.55rem; border-radius: 100px; font-size: 0.68rem; font-weight: 800; }

/* EMPTY STATE */
.empty-box { background: #f9fafb; border: 2px dashed #e5e7eb; border-radius: 16px; padding: 2.5rem 1.25rem; text-align: center; }
.empty-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.empty-title { font-size: 1.05rem; font-weight: 800; color: #374151; margin-bottom: 0.3rem; }
.empty-text { color: #6b7280; font-size: 0.85rem; }

/* MARKET STRIP */
.market-strip { background: linear-gradient(90deg, #eff6ff, #f0f9ff); border: 1px solid #bfdbfe; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-around; flex-wrap: wrap; gap: 0.75rem; }
.market-item { text-align: center; }
.market-label { font-size: 0.65rem; color: #1e40af; font-weight: 800; text-transform: uppercase; }
.market-value { font-size: 1rem; font-weight: 900; color: #1e3a8a; }

/* FAQ CARD */
.faq-card { background: white; border-radius: 12px; padding: 1rem 1.15rem; margin-bottom: 0.6rem; border: 1px solid #e5e7eb; }
.faq-q { font-weight: 800; color: #111827; font-size: 0.9rem; margin-bottom: 0.35rem; }
.faq-a { color: #4b5563; font-size: 0.82rem; line-height: 1.55; }

/* AGENT CTA */
.agent-cta { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 16px; padding: 1.75rem 1.25rem; color: white; text-align: center; box-shadow: 0 15px 35px rgba(99,102,241,0.25); }

/* FOOTER */
.footer-box { text-align: center; color: #9ca3af; font-size: 0.75rem; padding: 2rem 1rem 1rem 1rem; border-top: 1px solid #e5e7eb; margin-top: 2rem; }

/* Mobile responsive */
@media (max-width: 768px) {
    .hero { padding: 1.5rem 1rem; border-radius: 16px; }
    .hero h1 { font-size: 1.5rem; letter-spacing: -0.5px; }
    .hero p { font-size: 0.85rem; margin-bottom: 0.85rem; }
    .hero-badge { font-size: 0.65rem; padding: 0.35rem 0.7rem; }
    .nav { padding: 0.6rem 0; margin-bottom: 1rem; }
    .nav-logo { font-size: 1.05rem; }
    .nav-tag { font-size: 0.62rem; padding: 0.25rem 0.6rem; }
    
    .form-card { padding: 0.95rem; border-radius: 12px; }
    .form-card-title { font-size: 0.88rem; margin-bottom: 0.7rem; }
    
    .property-image { height: 200px; font-size: 4.5rem; }
    .property-title { font-size: 1.15rem; }
    .property-location { font-size: 0.9rem; }
    .property-stat-value { font-size: 1.05rem; }
    .property-stat-label { font-size: 0.68rem; }
    
    .price-value { font-size: 2.4rem; letter-spacing: -1px; }
    .price-label { font-size: 0.68rem; }
    .price-egp { font-size: 0.95rem; }
    .monthly-value { font-size: 1.3rem; }
    
    .metric-value { font-size: 1rem; }
    .metric-label { font-size: 0.58rem; }
    
    .market-strip { flex-direction: column; gap: 0.5rem; padding: 0.75rem; }
    .market-item { width: 100%; text-align: center; padding: 0.5rem 0; border-bottom: 1px solid #e0e7ff; }
    .market-item:last-child { border-bottom: none; }
    .market-label { font-size: 0.62rem; }
    .market-value { font-size: 0.95rem; }
    
    .faq-card { padding: 0.85rem 1rem; }
    .faq-q { font-size: 0.85rem; }
    .faq-a { font-size: 0.78rem; }
    
    .agent-cta { padding: 1.5rem 1rem; }
    .agent-cta h3 { font-size: 1.1rem; }
    .agent-cta p { font-size: 0.82rem; }
    
    .footer-box { font-size: 0.7rem; padding: 1.5rem 0.75rem 0.75rem 0.75rem; }
    
    .main .block-container { padding: 0.75rem 0.75rem 2rem 0.75rem !important; }
}
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
    '<div class="hero-badges">'
    '<span class="hero-badge">🎯 Accuracy ' + r2_str + '</span>'
    '<span class="hero-badge">📊 Avg Error ' + mape_str + '%</span>'
    '<span class="hero-badge">🏙️ ' + cities_str + ' Cities</span>'
    '<span class="hero-badge">📊 ' + total_str + ' Real Listings</span>'
    '</div></div>'
)
st.markdown(hero_html, unsafe_allow_html=True)


# ============================================================
# 2-COLUMN: FORM (left) + PREVIEW (right)
# ============================================================
col_left, col_right = st.columns([6, 4], gap="large")

with col_left:
    # STEP 1: LOCATION
    step1_title = '<div class="form-card-title"><div class="form-step">1</div>📍 Location</div>'
    st.markdown('<div class="form-card">' + step1_title, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        city = st.selectbox("City", categories["city"], key="s_city")
    with c2:
        district = st.selectbox("District", categories["district"], key="s_district")

    # Compound options with search fallback
    _all_compounds = categories["compound"]
    _seen = set()
    _clean_compounds = []
    for _c in _all_compounds:
        _ck = str(_c).strip().lower()
        if _ck and _ck not in _seen:
            _seen.add(_ck)
            _clean_compounds.append(str(_c).strip())
    _clean_compounds.sort(key=str.lower)
    compound_options = ["None"] + _clean_compounds
    compound = st.selectbox(
        "Known Compound (optional) — skip if unknown",
        compound_options,
        key="s_compound",
        help="Many areas are districts, not compounds. Try the District field first (e.g., Madinaty, Rehab)."
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 2: SIZE & ROOMS
    step2_title = '<div class="form-card-title"><div class="form-step">2</div>📐 Size & Rooms</div>'
    st.markdown('<div class="form-card">' + step2_title, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.slider("Area (m²)", 80, 500, 150, 5, key="s_area")
    with c2:
        bedrooms = st.selectbox("Bedrooms", ["1","2","3","4","5","6"], index=2, key="s_beds")
    with c3:
        bathrooms = st.slider("Bathrooms", 1, 5, 2, key="s_baths")

    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 3: AMENITIES
    step3_title = '<div class="form-card-title"><div class="form-step">3</div>✨ Features & Amenities</div>'
    st.markdown('<div class="form-card">' + step3_title, unsafe_allow_html=True)

    AMENITY_UI = {
        "Balcony": "BA", "Built-in Wardrobes": "BW", "Covered Parking": "CP",
        "Private Garden": "PG", "Shared Pool": "SP", "Security": "SE",
        "Air Conditioning": "AC", "Kitchen": "BK", "Maid Room": "MR",
        "Storage": "ST", "Children Area": "CO", "Gym": "GY",
    }
    selected_amenities = []
    cols = st.columns(3)
    for i, (label, code) in enumerate(AMENITY_UI.items()):
        with cols[i % 3]:
            if st.checkbox(label, value=(code in ["BA", "SE"]), key=f"am_{code}"):
                selected_amenities.append(code)

    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 4: DESCRIPTION
    step4_title = '<div class="form-card-title"><div class="form-step">4</div>📝 Description (optional)</div>'
    st.markdown('<div class="form-card">' + step4_title, unsafe_allow_html=True)

    description = st.text_area(
        "Description",
        placeholder="Example: Sea view apartment, fully furnished, super lux",
        height=80, key="s_desc",
        label_visibility="collapsed",
    )

    sentiment = analyze_sentiment(description) if description else None
    if sentiment and sentiment['label'] != 'neutral':
        emoji = get_sentiment_emoji(sentiment['label'])
        color = "#10b981" if sentiment['label'] == 'positive' else "#ef4444"
        score_str = f'{sentiment["score"]:+.2f}'
        source = sentiment.get('source', 'keywords')
        source_label = "AraBERT" if source in ['araBERT', 'blended'] else "Keywords"
        sent_html = (
            '<div style="background:' + color + '10;border-left:4px solid ' + color
            + ';padding:0.6rem 0.85rem;border-radius:8px;margin-top:0.5rem;color:' + color
            + ';font-weight:600;font-size:0.82rem;">'
            + emoji + ' ' + sentiment["label"].title() + ' sentiment (' + score_str + ')'
            + ' <span style="opacity:0.7;font-size:0.72rem;">via ' + source_label + '</span>'
            + '</div>'
        )
        st.markdown(sent_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# RIGHT: LIVE PREVIEW
with col_right:
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
        '<div class="property-stat"><div class="property-stat-value">' + compound_text + '</div><div class="property-stat-label">Compound</div></div>'
        '<div class="property-stat"><div class="property-stat-value">Real</div><div class="property-stat-label">Data</div></div>'
        '</div></div></div>'
    )
    st.markdown(preview_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🔮  Get Price Estimate", type="primary", use_container_width=True)



# ============================================================
# BUILD FEATURES
# ============================================================
CITY_GPS = {
    "Cairo": (30.0444, 31.2357), "Giza": (30.0131, 31.2089),
    "Alexandria": (31.2001, 29.9187), "Red Sea": (27.2579, 33.8116),
    "North Coast": (31.0906, 27.9407), "Suez": (29.9737, 32.5263),
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


if predict_btn:
    errors = validate_input(area, bedrooms, bathrooms, city, district, compound)
    if errors:
        st.error("WARNING: " + " | ".join(errors))
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

        res_left, res_right = st.columns([5, 5], gap="large")

        with res_left:
            price_html = (
                '<div class="price-hero">'
                '<div class="price-label">Estimated Market Value</div>'
                '<div class="price-value">' + f'{price/1_000_000:.2f}M' + '</div>'
                '<div class="price-egp">' + f'{price:,.0f}' + ' EGP</div>'
                '<div class="price-range-bar"><div class="price-range-fill"></div></div>'
                '<div class="price-range-labels">'
                '<span>' + format_price(result['lower_bound']) + '</span>'
                '<span>' + format_price(result['upper_bound']) + '</span>'
                '</div></div>'
            )
            st.markdown(price_html, unsafe_allow_html=True)

            monthly_rate = 0.10 / 12
            n_payments = 20 * 12
            down_payment = price * 0.20
            loan_amount = price - down_payment
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -n_payments)

            monthly_html = (
                '<div class="monthly-card">'
                '<div class="monthly-title">Est. Monthly Payment</div>'
                '<div class="monthly-value">' + f'{monthly_payment:,.0f}' + ' EGP</div>'
                '<div class="monthly-detail">20% down, 20 years, 10% interest</div>'
                '</div>'
            )
            st.markdown(monthly_html, unsafe_allow_html=True)

            if PDF_AVAILABLE:
                try:
                    pdf_buf = generate_pdf_report(
                        {'price': price, 'lower_bound': result['lower_bound'],
                         'upper_bound': result['upper_bound'], 'price_per_sqm': ppm},
                        {'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
                         'city': city, 'town': 'n/a', 'district': district,
                         'subdistrict': compound, 'furnished': 'n/a',
                         'completion_status': 'n/a'},
                        {'model_name': metadata['model_name'], 'r2': m['r2'],
                         'mape': m['mape'], 'n_train': metadata['training_info']['n_train']},
                    )
                    st.download_button(
                        "Download PDF Report", data=pdf_buf,
                        file_name="property_report.pdf",
                        mime="application/pdf", use_container_width=True,
                    )
                except Exception:
                    pass

            share_text = f"Estimated property price: {price:,.0f} EGP for {area} m2 in {district}, {city}."
            share_url = "https://wa.me/?text=" + share_text.replace(' ', '%20')
            share_html = (
                '<a href="' + share_url + '" target="_blank" style="display:block;width:100%;text-align:center;'
                'background:#25D366;color:white;padding:0.85rem 1.5rem;border-radius:12px;font-weight:800;'
                'text-decoration:none;font-size:0.95rem;margin-top:0.5rem;">'
                'Share on WhatsApp</a>'
            )
            st.markdown(share_html, unsafe_allow_html=True)

        with res_right:
            district_ppm = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
            diff_pct = ((ppm - district_ppm) / district_ppm * 100) if district_ppm else 0
            arrow = "🟢" if diff_pct >= 0 else "🔴"

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f'{ppm:,.0f}' + '</div><div class="metric-label">Price / m2</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f'{district_ppm:,.0f}' + '</div><div class="metric-label">District Avg</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f'{diff_pct:+.1f}' + '%</div><div class="metric-label">vs District</div></div>', unsafe_allow_html=True)

            city_growth = {"Cairo": 15.2, "Giza": 17.2, "Alexandria": 13.1, "Red Sea": 12.0, "North Coast": 14.5, "Suez": 16.0}
            growth = city_growth.get(city, 15.0)
            history_html = (
                '<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:12px;padding:0.85rem;margin-top:0.75rem;">'
                '<div style="font-weight:800;color:#78350f;font-size:0.8rem;">12-Month Trend</div>'
                '<div style="color:#92400e;font-size:0.72rem;margin-top:0.15rem;">Prices in ' + city + ' rose ' + f'{growth:.1f}' + '% this year</div>'
                '<div style="font-size:1.3rem;font-weight:900;color:#78350f;margin-top:0.35rem;">+' + f'{growth:.1f}' + '%</div>'
                '</div>'
            )
            st.markdown(history_html, unsafe_allow_html=True)



        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 🔍 Dive Deeper")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "🧠 Why This Price", "🗺️ Market", "🏘️ Similar",
            "⚖️ Compare", "💰 Investment", "📈 Forecast", "📍 Map"
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
                    text=[f"{v:+.3f}" for v in sv[idx]], textposition='outside',
                ))
                fig.update_layout(height=400, margin=dict(l=10, r=40, t=20, b=20),
                                   xaxis_title="Impact on price", showlegend=False, plot_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Green = increases price | Red = decreases price")
            except Exception as e:
                st.error(f"SHAP error: {e}")

        with tab2:
            st.markdown("#### District Price Ranking")
            price_data = mappings['price_mappings']['district_price_per_sqm']
            ppm_series = pd.Series(price_data).sort_values(ascending=True).tail(20)
            fig = go.Figure(go.Bar(
                x=ppm_series.values, y=ppm_series.index, orientation='h',
                marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
                text=[f"{v:,.0f}" for v in ppm_series.values], textposition='outside',
            ))
            fig.update_layout(height=600, margin=dict(l=10, r=60, t=20, b=20),
                              xaxis_title="EGP per m2")
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.caption("Most similar properties from real listings")
            try:
                # Filter similar properties by price range (±30% of estimate)
                price_range = (result['lower_bound'] * 0.85, result['upper_bound'] * 1.15)
                recs = recommend_similar_properties(
                    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
                    city=city, district=district,
                    compound=compound if compound != "None" else "None",
                    top_n=5, price_range=price_range,
                )
                if recs:
                    st.caption(f"Found {len(recs)} similar properties")
                    for i, r in enumerate(recs, 1):
                        sim_pct = r['similarity'] * 100
                        bd = "Studio" if r.get('is_studio') == 1 else f"{r['bedrooms_clean']} BR"
                        card_html = (
                            '<div class="sim-card">'
                            '<div style="display:flex;justify-content:space-between;align-items:center;">'
                            '<div>'
                            '<b style="color:#6366f1;">#' + str(i) + '</b> '
                            '<b>' + f"{r['area_value']:.0f}" + ' m2 | ' + bd + '</b>'
                            '<div style="color:#6b7280;font-size:0.82rem;margin-top:0.2rem;">' + r['city'] + ' - ' + r['district'] + '</div>'
                            '<div style="margin-top:0.3rem;"><span class="sim-match">' + f'{sim_pct:.0f}' + '% match</span></div>'
                            '</div>'
                            '<div style="text-align:right;">'
                            '<div style="font-size:1.3rem;font-weight:800;color:#10b981;">' + f"{r['predicted_price']/1e6:.2f}" + 'M</div>'
                            '<div style="font-size:0.68rem;color:#9ca3af;">EGP</div>'
                            '</div></div></div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Recommendation error: {e}")

        with tab4:
            st.caption("Compare this property with an alternative")
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**Property A (current)**")
                a_html = (
                    '<div class="metric-card">'
                    '<div class="metric-value" style="color:#10b981;">' + f'{price:,.0f}' + ' EGP</div>'
                    '<div style="margin-top:0.5rem;font-size:0.82rem;">'
                    'Area: ' + f'{area}' + ' m2<br>'
                    'Bedrooms: ' + str(bedrooms) + '<br>'
                    'Bathrooms: ' + str(bathrooms) + '<br>'
                    'Location: ' + city + ' - ' + district + '</div></div>'
                )
                st.markdown(a_html, unsafe_allow_html=True)
            with colB:
                st.markdown("**Property B (alternative)**")
                b_area = st.number_input("Area (m2)", 40, 500, 200, 5, key="cmp_area")
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
                    '<div style="margin-top:0.5rem;font-size:0.82rem;">'
                    'Area: ' + f'{b_area}' + ' m2<br>'
                    'Bedrooms: ' + b_bedrooms + '<br>'
                    'Bathrooms: ' + str(b_bathrooms) + '<br>'
                    'Location: ' + b_city + ' - ' + b_district + '</div></div>'
                )
                st.markdown(b_html, unsafe_allow_html=True)

            diff = price - price_b
            if diff < 0:
                st.success(f"Property A is cheaper by {abs(diff):,.0f} EGP")
            else:
                st.info(f"Property B is cheaper by {abs(diff):,.0f} EGP")

        with tab5:
            st.markdown("#### Investment ROI (5 Years)")
            roi = calculate_roi(price, years=5)
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['roi_pct']:.0f}" + '%</div><div class="metric-label">Total ROI</div></div>', unsafe_allow_html=True)
            with i2:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['annualized_roi_pct']:.1f}" + '%</div><div class="metric-label">Annualized</div></div>', unsafe_allow_html=True)
            with i3:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['total_rental_income']/1e6:.2f}" + 'M</div><div class="metric-label">Rental</div></div>', unsafe_allow_html=True)
            with i4:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['appreciation_gain']/1e6:.2f}" + 'M</div><div class="metric-label">Appreciation</div></div>', unsafe_allow_html=True)

            years_arr = np.arange(6)
            rental = [price * 0.005 * 12 * y / 1e6 for y in years_arr]
            appr = [(price * (1.12 ** y) - price) / 1e6 for y in years_arr]
            fig_roi = go.Figure()
            fig_roi.add_trace(go.Bar(x=years_arr, y=rental, name='Rental Income', marker_color='#10b981'))
            fig_roi.add_trace(go.Bar(x=years_arr, y=appr, name='Appreciation', marker_color='#6366f1'))
            fig_roi.update_layout(barmode='stack', height=320, xaxis_title="Year", yaxis_title="Million EGP", plot_bgcolor='white')
            st.plotly_chart(fig_roi, use_container_width=True)

        # ---------- TAB 6: FORECAST ----------
        with tab6:
            st.markdown("#### 📈 12-Month Price Forecast")
            st.caption("Prophet-based time series forecast per city")

            forecasts = _load_forecasts()

            if forecasts is None:
                st.warning("⚠️ Time series model not available")
            else:
                import plotly.graph_objects as go

                # Chart: Historical + Forecast for all cities
                fig_ts = go.Figure()

                colors_ts = [
                    '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                    '#ec4899', '#06b6d4', '#84cc16', '#f97316',
                ]

                for i, (city_name, data) in enumerate(forecasts.items()):
                    color = colors_ts[i % len(colors_ts)]
                    hist = pd.DataFrame(data['historical'])
                    preds = pd.DataFrame(data['all_predictions'])

                    # Historical line
                    fig_ts.add_trace(go.Scatter(
                        x=hist['ds'], y=hist['y'],
                        mode='lines',
                        name=f"{city_name} (hist)",
                        line=dict(color=color, width=1.5),
                        legendgroup=city_name,
                    ))

                    # Forecast line (dashed)
                    forecast_only = preds[preds['ds'] > hist['ds'].max()]
                    fig_ts.add_trace(go.Scatter(
                        x=forecast_only['ds'], y=forecast_only['yhat'],
                        mode='lines',
                        name=f"{city_name} (forecast)",
                        line=dict(color=color, width=2.5, dash='dash'),
                        legendgroup=city_name,
                    ))

                fig_ts.update_layout(
                    height=550,
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis_title="Date",
                    yaxis_title="Price (EGP/m²)",
                    hovermode='x unified',
                    plot_bgcolor='white',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                )

                # Add vertical line for "today"
                fig_ts.add_vline(
                    x=pd.Timestamp('2026-01-01').timestamp() * 1000,
                    line_dash="dot",
                    line_color="gray",
                    annotation_text="Today",
                    annotation_position="top",
                )

                st.plotly_chart(fig_ts, use_container_width=True)

                # Table: Growth per city
                st.markdown("#### 📊 Expected 12-Month Growth")
                growth_data = []
                for city_name, data in sorted(
                    forecasts.items(),
                    key=lambda x: -x[1]['growth_12m_pct']
                ):
                    growth_data.append({
                        'City': city_name,
                        'Current (EGP/m²)': f"{data['current_price']:,.0f}",
                        'Forecast +12M': f"{data['forecast_12m']:,.0f}",
                        'Growth': f"+{data['growth_12m_pct']:.1f}%",
                    })

                growth_df = pd.DataFrame(growth_data)
                st.dataframe(growth_df, hide_index=True, use_container_width=True)

                # Summary metrics
                avg_growth = np.mean([d['growth_12m_pct'] for d in forecasts.values()])
                best_city = max(forecasts.items(), key=lambda x: x[1]['growth_12m_pct'])

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">+{avg_growth:.1f}%</div><div class="metric-label">Avg Growth</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{best_city[0]}</div><div class="metric-label">Best City</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(forecasts)}</div><div class="metric-label">Cities Covered</div></div>', unsafe_allow_html=True)

        # ---------- TAB 7: INTERACTIVE MAP ----------
        with tab7:
            st.markdown("#### 📍 Interactive Property Map")
            st.caption(f"Real listings from PropertyFinder Egypt with location & pricing")

            map_data = _load_map_data()

            if map_data is None:
                st.warning("⚠️ Map data not available")
            else:
                import folium
                from streamlit_folium import st_folium

                # Filters
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    cities_in_map = sorted(map_data['city'].unique())
                    selected_cities = st.multiselect(
                        "Filter by City",
                        cities_in_map,
                        default=cities_in_map,
                        key="map_cities",
                    )

                with col_b:
                    if len(selected_cities) > 0:
                        filtered = map_data[map_data['city'].isin(selected_cities)]
                    else:
                        filtered = map_data

                    if len(filtered) > 0:
                        price_min = float(filtered['price_m'].min())
                        price_max = float(filtered['price_m'].max())
                    else:
                        price_min, price_max = 0.0, 50.0

                    price_range = st.slider(
                        "Price Range (Million EGP)",
                        min_value=0.0,
                        max_value=float(map_data['price_m'].max()),
                        value=(price_min, price_max),
                        step=0.5,
                        key="map_price_range",
                    )

                with col_c:
                    size_max = int(map_data['size'].max())
                    size_range = st.slider(
                        "Size Range (m²)",
                        min_value=40,
                        max_value=size_max,
                        value=(80, min(400, size_max)),
                        key="map_size_range",
                    )

                # Apply filters
                filtered_map = map_data[
                    (map_data['city'].isin(selected_cities)) &
                    (map_data['price_m'] >= price_range[0]) &
                    (map_data['price_m'] <= price_range[1]) &
                    (map_data['size'] >= size_range[0]) &
                    (map_data['size'] <= size_range[1])
                ].copy()

                st.caption(f"📍 Showing **{len(filtered_map):,}** properties")

                if len(filtered_map) == 0:
                    st.warning("⚠️ No properties match the filters")
                else:
                    # Color by price
                    def get_color(p):
                        if p < 5: return '#43A047'
                        elif p < 10: return '#FB8C00'
                        else: return '#E53935'

                    # Center map on Egypt
                    m = folium.Map(
                        location=[27, 31],
                        zoom_start=6,
                        tiles='cartodbpositron',
                    )

                    # Add markers
                    for _, row in filtered_map.iterrows():
                        color = get_color(row['price_m'])
                        radius = 6 + min(row['price_m'] / 3, 10)

                        popup_html = f"""
                        <div style="font-family: Arial; width: 200px;">
                            <h4 style="margin: 0 0 5px 0; color: #6366f1;">{row['district']}</h4>
                            <p style="margin: 3px 0; font-size: 11px; color: #666;">
                                📍 {row['city']} · {row['district']}
                            </p>
                            <hr style="margin: 5px 0;">
                            <p style="margin: 3px 0; font-size: 12px;">
                                📐 <b>{int(row['size'])} m²</b>
                            </p>
                            <p style="margin: 3px 0; font-size: 12px;">
                                🛏️ {int(row['bedrooms']) if pd.notna(row['bedrooms']) else 'N/A'} BR
                                · 🚿 {int(row['bathrooms']) if pd.notna(row['bathrooms']) else 'N/A'} BA
                            </p>
                            <p style="margin: 8px 0 3px 0; font-size: 16px; color: #10b981; font-weight: bold;">
                                {row['price_m']:.2f}M EGP
                            </p>
                            <p style="margin: 0; font-size: 10px; color: #888;">
                                {row['price_per_sqm']:,.0f} EGP/m²
                            </p>
                        </div>
                        """

                        folium.CircleMarker(
                            location=[row['latitude'], row['longitude']],
                            radius=radius,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.65,
                            weight=1.5,
                            popup=folium.Popup(popup_html, max_width=220),
                            tooltip=f"{row['district']}: {row['price_m']:.2f}M EGP",
                        ).add_to(m)

                    st_folium(m, width=None, height=600, returned_objects=[])

                    # Legend
                    st.markdown("""
                    <div style="background:#f9fafb; padding:1rem; border-radius:10px; margin-top:0.75rem; display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center;">
                        <div><span style="color:#43A047; font-size:1.5rem;">●</span> Under 5M EGP</div>
                        <div><span style="color:#FB8C00; font-size:1.5rem;">●</span> 5M - 10M EGP</div>
                        <div><span style="color:#E53935; font-size:1.5rem;">●</span> Over 10M EGP</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Stats per city
                    st.markdown("#### 📊 Properties by City")
                    city_stats = filtered_map.groupby('city').agg({
                        'price_m': ['count', 'mean', 'min', 'max']
                    }).round(2)
                    city_stats.columns = ['Count', 'Avg Price (M)', 'Min (M)', 'Max (M)']
                    city_stats = city_stats.sort_values('Count', ascending=False)
                    st.dataframe(city_stats, use_container_width=True)

else:
    empty_html = (
        '<div class="empty-box">'
        '<div class="empty-icon">🏠</div>'
        '<div class="empty-title">Ready to estimate your property</div>'
        '<div class="empty-text">Fill in the details above and click <b>Get Price Estimate</b></div>'
        '</div>'
    )
    st.markdown(empty_html, unsafe_allow_html=True)



# ============================================================
# MARKET STATS STRIP
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

city_ppm_all = mappings['price_mappings']['city_price_per_sqm']
top_cities = sorted(city_ppm_all.items(), key=lambda x: -x[1])[:3]
avg_ppm = mappings['price_mappings']['global_mean_ppm']

market_html = (
    '<div class="market-strip">'
    '<div class="market-item"><div class="market-label">Market Avg</div><div class="market-value">' + f'{avg_ppm:,.0f}' + ' EGP/m2</div></div>'
    '<div class="market-item"><div class="market-label">Top City</div><div class="market-value">' + top_cities[0][0] + '</div></div>'
    '<div class="market-item"><div class="market-label">Data Source</div><div class="market-value">PropertyFinder</div></div>'
    '</div>'
)
st.markdown(market_html, unsafe_allow_html=True)


# ============================================================
# FAQ CARDS
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## ❓ Frequently Asked Questions")

faq_items = [
    ("Is this data real?",
     "Yes. Our model is trained on 7,749 real property listings from PropertyFinder Egypt - the largest real estate platform in Egypt. Every listing has verified location, GPS coordinates, size, rooms, and amenities."),
    ("How accurate are the estimates?",
     "The model achieves 68.4% accuracy (R-squared = 0.68) with an average error margin of 18.4%. This is honest performance on real market data - many listings differ in condition, floor, view, and negotiation room, which are not captured in the data."),
    ("Can I use this as an official appraisal?",
     "No. This is an AI estimation tool for reference and research purposes. For official property valuation - especially for buying, selling, or legal matters - please consult a certified real estate appraiser."),
    ("Which cities are covered?",
     "The model covers 9 Egyptian cities: Cairo, Giza, Alexandria, Red Sea, North Coast, Suez, Qalyubia, Matrouh, and Al Daqahlya - with 43 districts and 890 compounds."),
    ("How does the AI calculate the price?",
     "We use XGBoost, a powerful gradient-boosting algorithm. It analyzes 64 features including size, location, GPS coordinates, amenities, and NLP-extracted keywords from listing titles. Every prediction comes with a SHAP explanation showing what drove the price."),
    ("Is my data stored anywhere?",
     "We only log anonymized predictions (area, city, predicted price) to monitor model performance. No personal information is collected."),
]

faq_css = """<style>
details.faq-item {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 0;
    margin-bottom: 0.6rem;
    overflow: hidden;
}
details.faq-item summary {
    padding: 1rem 1.15rem;
    cursor: pointer;
    list-style: none;
    font-weight: 800;
    color: #111827;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
details.faq-item summary::-webkit-details-marker { display: none; }
details.faq-item summary::before {
    content: '+';
    background: #ede9fe;
    color: #6366f1;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 1.1rem;
    flex-shrink: 0;
    transition: all 0.2s;
}
details.faq-item[open] summary::before {
    content: '-';
    background: #6366f1;
    color: white;
}
details.faq-item[open] summary {
    border-bottom: 1px solid #f3f4f6;
}
details.faq-item .faq-answer {
    padding: 0.9rem 1.15rem 1.1rem 3.15rem;
    color: #4b5563;
    font-size: 0.85rem;
    line-height: 1.6;
}
</style>"""

st.markdown(faq_css, unsafe_allow_html=True)

for i, (question, answer) in enumerate(faq_items, 1):
    faq_html = (
        '<details class="faq-item">'
        '<summary>' + f'{i:02d}' + '&nbsp;&nbsp;' + question + '</summary>'
        '<div class="faq-answer">' + answer + '</div>'
        '</details>'
    )
    st.markdown(faq_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# AGENT CTA
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

agent_html = (
    '<div class="agent-cta">'
    '<div style="font-size:2rem;margin-bottom:0.35rem;">🤝</div>'
    '<h3 style="font-size:1.3rem;font-weight:900;margin:0 0 0.5rem 0;">Want a Professional Valuation?</h3>'
    '<p style="opacity:0.95;font-size:0.88rem;margin:0 0 1.25rem 0;">Our AI gives fast estimates. For certified appraisals, connect with a trusted local real estate agent.</p>'
    '<div style="display:flex;justify-content:center;gap:0.5rem;flex-wrap:wrap;">'
    '<a href="https://www.propertyfinder.eg" target="_blank" style="background:white;color:#6366f1;padding:0.7rem 1.25rem;border-radius:100px;font-weight:800;text-decoration:none;font-size:0.85rem;">Browse PropertyFinder</a>'
    '<a href="https://wa.me/?text=Hi%2C%20I%20need%20a%20property%20valuation" target="_blank" style="background:rgba(255,255,255,0.2);color:white;padding:0.7rem 1.25rem;border-radius:100px;font-weight:800;text-decoration:none;font-size:0.85rem;border:1px solid rgba(255,255,255,0.3);">Contact an Agent</a>'
    '</div></div>'
)
st.markdown(agent_html, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
footer_html = (
    '<div class="footer-box">'
    '<b>Smart House Price Predictor</b> v11.0 - '
    + metadata['model_name'] + ' - '
    + f"R2 {m['r2']:.4f}" + ' - '
    + f"MAPE {m['mape']:.2f}%" + '<br>'
    'Trained on <b>' + f"{metadata['training_info']['n_total']:,}" + ' real property listings</b> from PropertyFinder Egypt'
    '<br><br>'
    'AI estimation tool - not a certified appraisal.'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
