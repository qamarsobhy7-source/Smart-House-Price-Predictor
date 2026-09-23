"""Smart House Price Predictor - Modern UI v8.0 (Zillow/Airbnb inspired)"""
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
    calculate_roi, recommend_similar_properties, compare_properties,
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


# ============================================================
# MODERN CSS
# ============================================================
st.markdown("""
<style>
    * { font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif; }

    .main { padding: 0 !important; }
    .main .block-container {
        max-width: 1300px;
        padding: 1.5rem 2rem 3rem 2rem;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ============ HERO ============ */
    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 40%, #ec4899 100%);
        padding: 3rem 2rem 2.5rem 2rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 24px 60px rgba(99, 102, 241, 0.25);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -100px; right: -100px;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.15), transparent 70%);
        border-radius: 50%;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 900;
        margin: 0 0 0.5rem 0;
        letter-spacing: -1px;
        line-height: 1.15;
        position: relative;
    }
    .hero p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0 0 1.5rem 0;
        position: relative;
    }
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        position: relative;
    }
    .hero-badge {
        background: rgba(255,255,255,0.22);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* ============ SECTION CARDS ============ */
    .section-card {
        background: white;
        border-radius: 18px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }
    .section-card:hover {
        border-color: #c7d2fe;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08);
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
    }
    .step-badge {
        width: 32px; height: 32px; line-height: 32px;
        text-align: center;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.95rem;
        flex-shrink: 0;
    }
    .section-title-text {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
    }

    /* ============ PREVIEW CARD (sticky sidebar) ============ */
    .preview-wrap {
        position: sticky;
        top: 1rem;
    }
    .preview-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
    }
    .preview-image {
        height: 140px;
        border-radius: 14px;
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 50%, #f0abfc 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .preview-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .preview-location {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .preview-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.9rem;
    }
    .preview-row:last-child { border-bottom: none; }
    .preview-label { color: #64748b; }
    .preview-value { color: #0f172a; font-weight: 600; }

    /* ============ PRICE RESULT ============ */
    .price-result {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 2rem 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
        margin-top: 1rem;
    }
    .price-result .label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.9;
        font-weight: 700;
    }
    .price-result .value {
        font-size: 3rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.5rem 0;
        letter-spacing: -2px;
    }
    .price-result .egp {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    .price-result .range {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.25);
        font-size: 0.85rem;
        opacity: 0.95;
    }

    /* ============ MINI METRIC ============ */
    .mini-metric {
        background: #f8fafc;
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #f1f5f9;
        margin-top: 0.75rem;
    }
    .mini-metric .val {
        font-size: 1.4rem;
        font-weight: 800;
        color: #6366f1;
        line-height: 1;
    }
    .mini-metric .lbl {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.4rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ============ CTA BUTTON ============ */
    .stButton > button[kind="primary"] {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 1.1rem 2rem;
        font-size: 1.1rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        box-shadow: 0 12px 28px rgba(99, 102, 241, 0.35);
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 36px rgba(99, 102, 241, 0.45);
    }

    /* ============ TABS ============ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: white;
        padding: 0.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 700;
        font-size: 0.88rem;
        color: #64748b;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }

    /* ============ EMPTY STATE ============ */
    .empty-state {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border: 2px dashed #cbd5e1;
        border-radius: 20px;
        padding: 3rem 1.5rem;
        text-align: center;
        color: #64748b;
    }
    .empty-state-icon { font-size: 3rem; margin-bottom: 0.75rem; }
    .empty-state-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.35rem;
    }
    .empty-state-text { font-size: 0.9rem; }

    /* ============ SIMILAR PROPERTY CARD ============ */
    .prop-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }
    .prop-card:hover {
        border-color: #c7d2fe;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.08);
    }
    .prop-match {
        display: inline-block;
        background: #ede9fe;
        color: #6366f1;
        padding: 0.15rem 0.6rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* ============ FOOTER ============ */
    .footer-note {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding: 2.5rem 0 1rem 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }

    /* ============ COMPARE CARD ============ */
    .compare-box {
        background: #f8fafc;
        border-radius: 14px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        height: 100%;
    }
    .compare-header {
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
        color: #6366f1;
    }

    /* ============ INPUT LABELS ============ */
    .input-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.35rem;
        margin-top: 0.75rem;
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
    st.error(f"Model loading error: {e}")
    st.stop()

m = metadata["metrics"]


# ============================================================
# HERO
# ============================================================
st.markdown(f"""
<div class="hero">
    <h1>Find Your Property's True Value</h1>
    <p>AI-powered estimates for the Egyptian real estate market</p>
    <div class="hero-badges">
        <span class="hero-badge">🎯 Accuracy {m['r2']:.4f}</span>
        <span class="hero-badge">📊 Avg Error {m['mape']:.2f}%</span>
        <span class="hero-badge">🏙️ {len(categories['city'])} Cities</span>
        <span class="hero-badge">📊 {metadata['training_info']['n_total']:,} Real Listings</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 2-COLUMN LAYOUT: Inputs (left) + Preview (right)
# ============================================================
col_left, col_right = st.columns([7, 5], gap="large")

with col_left:
    # ===== STEP 1: Location =====
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="step-badge">1</div>
            <div class="section-title-text">Where is the property?</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        city = st.selectbox("City", categories["city"], key="s_city")
    with c2:
        district = st.selectbox("District", categories["district"], key="s_district")

    compound_options = ["None"] + categories["compound"][:200]
    compound = st.selectbox("Compound (optional)", compound_options, key="s_compound")

    st.markdown("</div>", unsafe_allow_html=True)

    # ===== STEP 2: Size & Rooms =====
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="step-badge">2</div>
            <div class="section-title-text">Property size & rooms</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.slider("Area (sqm)", 40, 500, 150, 5, key="s_area")
    with c2:
        bedrooms = st.selectbox("Bedrooms", ["studio","1","2","3","4","5","6"], index=3, key="s_beds")
    with c3:
        bathrooms = st.slider("Bathrooms", 1, 5, 2, key="s_baths")

    st.markdown("</div>", unsafe_allow_html=True)

    # ===== STEP 3: Amenities =====
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="step-badge">3</div>
            <div class="section-title-text">Features & amenities</div>
        </div>
    """, unsafe_allow_html=True)

    AMENITY_UI = {
        "Balcony": "BA",
        "Built-in Wardrobes": "BW",
        "Covered Parking": "CP",
        "Private Garden": "PG",
        "Shared Pool": "SP",
        "Security": "SE",
        "Air Conditioning": "AC",
        "Kitchen": "BK",
        "Maid Room": "MR",
        "Storage": "ST",
        "Children Area": "CO",
        "Gym": "GY",
    }

    selected_amenities = []
    cols = st.columns(4)
    for i, (label, code) in enumerate(AMENITY_UI.items()):
        with cols[i % 4]:
            if st.checkbox(label, value=(code in ["BA", "SE"]), key=f"am_{code}"):
                selected_amenities.append(code)

    st.markdown("</div>", unsafe_allow_html=True)

    # ===== STEP 4: Description =====
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="step-badge">4</div>
            <div class="section-title-text">Additional details</div>
        </div>
    """, unsafe_allow_html=True)

    description = st.text_area(
        "Describe the property (optional)",
        placeholder="Example: Sea view apartment, fully furnished, super lux",
        height=90, key="s_desc",
        label_visibility="collapsed",
    )

    sentiment = analyze_sentiment(description) if description else None
    if sentiment and sentiment['label'] != 'neutral':
        emoji = "😊" if sentiment['label'] == 'positive' else "😟"
        color = "#10b981" if sentiment['label'] == 'positive' else "#ef4444"
        st.markdown(f"""
        <div style="background:{color}10; border-left:4px solid {color};
                    padding:0.7rem 1rem; border-radius:10px; margin-top:0.75rem;
                    color:{color}; font-weight:600; font-size:0.88rem;">
            {emoji} {sentiment['label'].title()} sentiment detected ({sentiment['score']:+.2f})
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RIGHT COLUMN: Live Preview + CTA
# ============================================================
with col_right:
    st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)

    # Live preview card
    bd_text = "Studio" if bedrooms == "studio" else f"{bedrooms} Bedrooms"
    area_text = f"{area} m²"

    st.markdown(f"""
    <div class="preview-card">
        <div class="preview-image">🏢</div>
        <div class="preview-title">{area_text} · {bd_text}</div>
        <div class="preview-location">📍 {city} → {district}</div>

        <div class="preview-row">
            <span class="preview-label">Bathrooms</span>
            <span class="preview-value">{bathrooms}</span>
        </div>
        <div class="preview-row">
            <span class="preview-label">Compound</span>
            <span class="preview-value">{compound if compound != "None" else "—"}</span>
        </div>
        <div class="preview-row">
            <span class="preview-label">Amenities</span>
            <span class="preview-value">{len(selected_amenities)} selected</span>
        </div>
        <div class="preview-row">
            <span class="preview-label">Data Source</span>
            <span class="preview-value">Real listings</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA button
    predict_btn = st.button("🔮  Get Price Estimate", type="primary",
                            use_container_width=True)

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
# RESULT SECTION
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

        # Result in 2 columns
        res_left, res_right = st.columns([5, 7], gap="large")

        with res_left:
            st.markdown(f"""
            <div class="price-result">
                <div class="label">Estimated Price</div>
                <div class="value">{price/1_000_000:.2f}M</div>
                <div class="egp">{price:,.0f} EGP</div>
                <div class="range">
                    📊 {format_price(result['lower_bound'])} — {format_price(result['upper_bound'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                        file_name=f"property_report_{int(price)}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception:
                    pass

        with res_right:
            district_ppm = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
            diff_pct = ((ppm - district_ppm) / district_ppm * 100) if district_ppm else 0
            arrow = "🟢" if diff_pct >= 0 else "🔴"

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="mini-metric"><div class="val">{ppm:,.0f}</div><div class="lbl">Price per m2</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="mini-metric"><div class="val">{district_ppm:,.0f}</div><div class="lbl">District Avg</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="mini-metric"><div class="val">{arrow} {diff_pct:+.1f}%</div><div class="lbl">vs District</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Dive Deeper")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Why This Price?",
            "Market",
            "Price Map",
            "Similar",
            "Compare",
            "Investment",
        ])

        # ---------- TAB 1: SHAP ----------
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
                clean_names = [feat_names[i].replace('num__','').replace('cat__','')
                                .replace('_',' ').title() for i in idx]
                colors = ['#10b981' if v > 0 else '#ef4444' for v in sv[idx]]

                fig = go.Figure(go.Bar(
                    x=sv[idx], y=clean_names, orientation='h',
                    marker_color=colors,
                    text=[f"{v:+.3f}" for v in sv[idx]],
                    textposition='outside',
                ))
                fig.update_layout(
                    height=420, margin=dict(l=10, r=40, t=20, b=20),
                    xaxis_title="Impact on price",
                    showlegend=False, plot_bgcolor='white',
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Green = increases price | Red = decreases price")
            except Exception as e:
                st.error(f"SHAP error: {e}")

        # ---------- TAB 2: Market ----------
        with tab2:
            st.markdown("#### District Price Ranking")
            price_data = mappings['price_mappings']['district_price_per_sqm']
            ppm_series = pd.Series(price_data).sort_values(ascending=True).tail(25)
            fig = go.Figure(go.Bar(
                x=ppm_series.values, y=ppm_series.index, orientation='h',
                marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
                text=[f"{v:,.0f}" for v in ppm_series.values],
                textposition='outside',
            ))
            fig.update_layout(height=650, margin=dict(l=10, r=60, t=20, b=20),
                              xaxis_title="EGP per m2")
            st.plotly_chart(fig, use_container_width=True)

        # ---------- TAB 3: Map ----------
        with tab3:
            st.markdown("#### Property Map")
            st.caption("Real listings from PropertyFinder Egypt")
            try:
                import folium
                from streamlit_folium import st_folium
                from predictor import load_recommendation_data

                rec_df = load_recommendation_data()
                if rec_df is not None and len(rec_df) > 0:
                    sample_df = rec_df.dropna(subset=['latitude', 'longitude']).sample(
                        n=min(400, len(rec_df)), random_state=42)

                    map_obj = folium.Map(location=[27, 31], zoom_start=6,
                                          tiles='cartodbpositron')

                    for _, row in sample_df.iterrows():
                        price_m = row['price'] / 1e6
                        if price_m < 3:
                            color = '#43A047'
                        elif price_m < 8:
                            color = '#FB8C00'
                        else:
                            color = '#E53935'

                        folium.CircleMarker(
                            location=[row['latitude'], row['longitude']],
                            radius=4, color=color, fill=True,
                            fill_opacity=0.7, weight=1,
                            popup=f"{row['city']} - {row['district']}<br>"
                                  f"{row['size']:.0f} m2<br>"
                                  f"{row['price']:,.0f} EGP",
                        ).add_to(map_obj)

                    if city in CITY_GPS:
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"Your property: {city}",
                            icon=folium.Icon(color='purple', icon='home'),
                        ).add_to(map_obj)

                    st_folium(map_obj, width=None, height=500, returned_objects=[])

                    st.markdown("""
                    <div style="background:#f8fafc; padding:1rem; border-radius:10px; margin-top:0.5rem;">
                        <b>Legend:</b>
                        <span style="color:#43A047;">Green</span> = Under 3M EGP
                        <span style="color:#FB8C00; margin-left:1rem;">Orange</span> = 3M-8M EGP
                        <span style="color:#E53935; margin-left:1rem;">Red</span> = Over 8M EGP
                        <span style="color:purple; margin-left:1rem;">Pin</span> = Your property
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Map error: {e}")

        # ---------- TAB 4: Similar ----------
        with tab4:
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
                        st.markdown(f"""
                        <div class="prop-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <b style="color:#6366f1; font-size:1.05rem;">#{i}</b>
                                    <b style="font-size:1.05rem;">{r['area_value']:.0f} m2 - {bd} - {r['bathrooms_clean']} bath</b>
                                    <div style="color:#64748b; font-size:0.9rem; margin-top:0.25rem;">
                                        {r['city']} - {r['district']}
                                    </div>
                                    <div style="margin-top:0.35rem;">
                                        <span class="prop-match">{sim_pct:.0f}% match</span>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    <div style="font-size:1.4rem; font-weight:800; color:#10b981;">
                                        {r['predicted_price']/1e6:.2f}M
                                    </div>
                                    <div style="font-size:0.75rem; color:#94a3b8;">EGP</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Recommendation error: {e}")

        # ---------- TAB 5: Compare ----------
        with tab5:
            st.caption("Compare this property with an alternative")

            colA, colB = st.columns(2)
            with colA:
                st.markdown("**Property A (current)**")
                st.markdown(f"""
                <div class="compare-box">
                    <div style="font-size:1.3rem; font-weight:800; color:#10b981;">
                        {price:,.0f} EGP
                    </div>
                    <div style="margin-top:0.75rem;">
                        Area: {area} m2<br>
                        Bedrooms: {bedrooms}<br>
                        Bathrooms: {bathrooms}<br>
                        Location: {city} - {district}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with colB:
                st.markdown("**Property B (alternative)**")
                b_area = st.number_input("Area (sqm)", 40, 500, 200, 5, key="cmp_area")
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

                st.markdown(f"""
                <div class="compare-box">
                    <div style="font-size:1.3rem; font-weight:800; color:#6366f1;">
                        {price_b:,.0f} EGP
                    </div>
                    <div style="margin-top:0.75rem;">
                        Area: {b_area} m2<br>
                        Bedrooms: {b_bedrooms}<br>
                        Bathrooms: {b_bathrooms}<br>
                        Location: {b_city} - {b_district}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            diff = price - price_b
            if diff < 0:
                st.success(f"Property A is cheaper by {abs(diff):,.0f} EGP")
            else:
                st.info(f"Property B is cheaper by {abs(diff):,.0f} EGP")

        # ---------- TAB 6: Investment ----------
        with tab6:
            st.markdown("#### Investment Analysis (5 Years)")
            roi = calculate_roi(price, years=5)

            c1, c2, c3, c4 = st.columns(4)
            metrics_list = [
                ("Total ROI", f"{roi['roi_pct']:.0f}%", "#6366f1"),
                ("Annualized", f"{roi['annualized_roi_pct']:.1f}%", "#10b981"),
                ("Rental (5y)", f"{roi['total_rental_income']/1e6:.2f}M", "#f59e0b"),
                ("Appreciation", f"{roi['appreciation_gain']/1e6:.2f}M", "#8b5cf6"),
            ]
            for col, (label, val, color) in zip([c1, c2, c3, c4], metrics_list):
                col.markdown(f'<div class="mini-metric"><div class="val" style="color:{color};">{val}</div><div class="lbl">{label}</div></div>', unsafe_allow_html=True)

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
    st.markdown("""
    <div class="empty-state" style="margin-top: 2rem;">
        <div class="empty-state-icon">Home</div>
        <div class="empty-state-title">Ready to estimate your property</div>
        <div class="empty-state-text">
            Fill in the details above and click <b>Get Price Estimate</b> to see the AI-powered valuation.
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown(f"""
<div class="footer-note">
    <b>Smart House Price Predictor</b> v8.0 &nbsp;&middot;&nbsp;
    {metadata['model_name']} &nbsp;&middot;&nbsp;
    R2 {m['r2']:.4f} &nbsp;&middot;&nbsp; MAPE {m['mape']:.2f}%
    <br>
    Trained on <b>{metadata['training_info']['n_total']:,} real property listings</b>
    from PropertyFinder Egypt
    <br><br>
    AI estimation tool - not a certified appraisal.
</div>
""", unsafe_allow_html=True)
