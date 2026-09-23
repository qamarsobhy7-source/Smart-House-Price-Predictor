"""Smart House Price Predictor - Streamlit App v6.0 (Modern Wizard UI)"""
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
    recommend_similar_properties, calculate_roi,
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
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
    .main .block-container {
        max-width: 920px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    #MainMenu, footer, header { visibility: hidden; }

    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 3rem 2rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.25);
    }
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .hero p { font-size: 1.05rem; opacity: 0.95; margin: 0; }

    .chip {
        display: inline-block;
        background: rgba(255, 255, 255, 0.22);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
        color: white;
    }

    .step-card {
        background: white;
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.75rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .step-number {
        display: inline-block;
        width: 32px; height: 32px; line-height: 32px;
        text-align: center;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border-radius: 10px;
        font-weight: 700;
        margin-right: 0.75rem;
        font-size: 0.95rem;
    }
    .step-title {
        display: inline-block;
        font-size: 1.15rem;
        font-weight: 700;
        color: #111827;
        vertical-align: middle;
    }

    .price-result {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 2.5rem 2rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 20px 50px rgba(16, 185, 129, 0.3);
    }
    .price-result .label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.9;
        font-weight: 600;
    }
    .price-result .value {
        font-size: 4rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.75rem 0;
        letter-spacing: -2px;
    }
    .price-result .egp { font-size: 1.3rem; opacity: 0.95; }
    .price-result .range {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.25);
        font-size: 0.95rem;
        opacity: 0.95;
    }

    .mini-metric {
        background: #f9fafb;
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #f3f4f6;
    }
    .mini-metric .val {
        font-size: 1.4rem;
        font-weight: 800;
        color: #6366f1;
        line-height: 1;
    }
    .mini-metric .lbl {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 0.4rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton > button[kind="primary"] {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 1.1rem 2rem;
        font-size: 1.15rem;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.45);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #f9fafb;
        padding: 0.4rem;
        border-radius: 14px;
        border: 1px solid #f3f4f6;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #6366f1 !important;
    }

    .footer-note {
        text-align: center;
        color: #9ca3af;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid #f3f4f6;
        margin-top: 3rem;
    }
    .soft-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
        margin: 2rem 0;
    }
    .similar-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
        border: 1px solid #e5e7eb;
    }
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

m = metadata["metrics"]


st.markdown(f"""
<div class="hero">
    <h1>Find Your Property's True Value</h1>
    <p>AI-powered estimates for Egyptian real estate</p>
    <div style="margin-top: 1.5rem;">
        <span class="chip">🎯 Accuracy {m['r2']:.4f}</span>
        <span class="chip">📊 Avg Error {m['mape']:.2f}%</span>
        <span class="chip">🏙️ 10 Cities</span>
        <span class="chip">🔧 {metadata['features']['total']} AI Features</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ===== STEP 1: Location =====
st.markdown("""
<div class="step-card">
    <span class="step-number">1</span>
    <span class="step-title">📍 Where is the property?</span>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    city = st.selectbox("City", categories["city"], key="s_city")
with c2:
    district = st.selectbox("District", categories["district"], key="s_district")

c3, c4 = st.columns(2)
with c3:
    town = st.selectbox("Area Type", categories["town"], key="s_town")
with c4:
    subdistrict = st.selectbox("Neighborhood", categories["subdistrict"], key="s_sub")


# ===== STEP 2: Size =====
st.markdown("""
<div class="step-card">
    <span class="step-number">2</span>
    <span class="step-title">📐 Property Size & Rooms</span>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    area = st.slider("Area (sqm)", 40, 500, 150, 5, key="s_area")
with c2:
    bedrooms = st.selectbox("Bedrooms", ["studio","1","2","3","4","5","6"],
                            index=3, key="s_beds")
with c3:
    bathrooms = st.slider("Bathrooms", 1, 5, 2, key="s_baths")


# ===== STEP 3: Status =====
st.markdown("""
<div class="step-card">
    <span class="step-number">3</span>
    <span class="step-title">🏗️ Current Status</span>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    furnished = st.selectbox("Furnished", categories["furnished"], key="s_furn")
with c2:
    completion_status = st.selectbox("Completion Status",
                                     categories["completion_status"], key="s_compl")

c1, c2, c3 = st.columns(3)
with c1:
    has_reception = st.checkbox("Reception Area", True, key="s_rec")
with c2:
    has_living = st.checkbox("Living Room", True, key="s_liv")
with c3:
    has_kitchen = st.checkbox("Kitchen", True, key="s_kit")


# ===== STEP 4: Description =====
st.markdown("""
<div class="step-card">
    <span class="step-number">4</span>
    <span class="step-title">✨ Additional Details</span>
</div>
""", unsafe_allow_html=True)

description = st.text_area(
    "Describe the property (optional)",
    placeholder="Example: Sea view apartment, fully furnished, super lux",
    height=80, key="s_desc",
    label_visibility="collapsed",
)

sentiment = analyze_sentiment(description) if description else None
if sentiment and sentiment['label'] != 'neutral':
    emoji = "😊" if sentiment['label'] == 'positive' else "😟"
    color = "#10b981" if sentiment['label'] == 'positive' else "#ef4444"
    st.markdown(f"""
    <div style="background:{color}10; border-left:4px solid {color};
                padding:0.75rem 1rem; border-radius:10px; margin:0.5rem 0;
                color:{color}; font-weight:600; font-size:0.9rem;">
        {emoji} {sentiment['label'].title()} sentiment detected ({sentiment['score']:+.2f})
    </div>
    """, unsafe_allow_html=True)


# ===== CTA =====
st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
predict_btn = st.button("🔮  Get Price Estimate", type="primary", use_container_width=True)


input_features = build_features(
    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
    city=city, town=town, district=district, subdistrict=subdistrict,
    furnished=furnished, completion_status=completion_status,
    has_reception=has_reception, has_living=has_living,
    has_kitchen=has_kitchen, description=description, mappings=mappings,
)


# ===== RESULT =====
if predict_btn:
    errors = validate_input(area, bedrooms, bathrooms, city, town,
                             district, subdistrict, furnished, completion_status)
    if errors:
        st.error("⚠️ " + " | ".join(errors))
    else:
        result = predict_with_confidence(model, input_features, m["mape"])
        price = result["price"]
        ppm = price / area
        dist_avg = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
        diff_pct = (ppm - dist_avg) / dist_avg * 100 if dist_avg else 0

        if MONITORING_AVAILABLE:
            try:
                log_prediction(area=area, bedrooms=bedrooms, bathrooms=bathrooms,
                                city=city, town=town, district=district,
                                predicted_price=price,
                                confidence_lower=result['lower_bound'],
                                confidence_upper=result['upper_bound'])
            except Exception:
                pass

        st.markdown(f"""
        <div class="price-result">
            <div class="label">Your Estimated Price</div>
            <div class="value">{price/1_000_000:.2f}M</div>
            <div class="egp">{price:,.0f} EGP</div>
            <div class="range">
                📊 Confidence Range: {format_price(result['lower_bound'])} — {format_price(result['upper_bound'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="mini-metric"><div class="val">{ppm:,.0f}</div><div class="lbl">Price per sqm</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="mini-metric"><div class="val">{dist_avg:,.0f}</div><div class="lbl">District Avg</div></div>', unsafe_allow_html=True)
        with c3:
            arrow = "🟢" if diff_pct >= 0 else "🔴"
            st.markdown(f'<div class="mini-metric"><div class="val">{arrow} {diff_pct:+.1f}%</div><div class="lbl">vs District Avg</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if PDF_AVAILABLE:
            try:
                pdf_buf = generate_pdf_report(
                    {'price': price, 'lower_bound': result['lower_bound'],
                     'upper_bound': result['upper_bound'], 'price_per_sqm': ppm},
                    {'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
                     'city': city, 'town': town, 'district': district,
                     'subdistrict': subdistrict, 'furnished': furnished,
                     'completion_status': completion_status},
                    {'model_name': metadata['model_name'], 'r2': m['r2'],
                     'mape': m['mape'], 'n_train': metadata['training_info']['n_train']},
                )
                st.download_button("📄  Download PDF Report", data=pdf_buf,
                    file_name=f"property_report_{int(price)}.pdf",
                    mime="application/pdf", use_container_width=True)
            except Exception:
                pass

        st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Dive Deeper Into the Analysis")

        tab1, tab2, tab3, tab4 = st.tabs([
            "🧠 Why This Price?",
            "🗺️ Market Insights",
            "🏘️ Find Similar",
            "💰 Investment",
        ])

        with tab1:
            st.caption("AI breakdown: which features pushed the price up or down")
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
                                   xaxis_title="Impact on price", showlegend=False,
                                   plot_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
                st.caption("🟢 Green = pushes price UP · 🔴 Red = pushes price DOWN")
            except Exception as e:
                st.error(f"SHAP error: {e}")

        with tab2:
            st.markdown("#### 🗺️ District Price Ranking")
            price_data = mappings['price_mappings']['district_price_per_sqm']
            ppm_series = pd.Series(price_data).sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=ppm_series.values, y=ppm_series.index, orientation='h',
                marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
                text=[f"{v:,.0f}" for v in ppm_series.values],
                textposition='outside',
            ))
            fig.update_layout(height=max(500, len(ppm_series)*18),
                              margin=dict(l=10, r=60, t=20, b=20),
                              xaxis_title="EGP per sqm")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 📈 12-Month Price Forecast")
            try:
                import joblib as _jl
                ts = _jl.load(Path(__file__).resolve().parent / "models" / "time_series_forecasts.joblib")
                fig2 = go.Figure()
                for city_name, data in ts.items():
                    hist = pd.DataFrame(data['historical'])
                    fut = pd.DataFrame(data['forecast'])
                    fig2.add_trace(go.Scatter(x=hist['ds'], y=hist['y'],
                                               mode='lines', name=f"{city_name} (hist)",
                                               line=dict(width=1.5)))
                    fig2.add_trace(go.Scatter(x=fut['ds'], y=fut['yhat'],
                                               mode='lines', name=f"{city_name} (forecast)",
                                               line=dict(width=2.5, dash='dash')))
                fig2.update_layout(height=450, margin=dict(l=10, r=20, t=20, b=20),
                                    xaxis_title="Date", yaxis_title="EGP/sqm",
                                    hovermode='x unified')
                st.plotly_chart(fig2, use_container_width=True)
            except Exception:
                pass

        with tab3:
            st.caption("Top 5 most similar properties from the dataset")
            try:
                recs = recommend_similar_properties(
                    area=area, bedrooms=bedrooms, bathrooms=bathrooms,
                    city=city, town=town, district=district,
                    subdistrict=subdistrict, furnished=furnished,
                    completion_status=completion_status, top_n=5,
                )
                if recs:
                    for i, r in enumerate(recs, 1):
                        sim = r['similarity'] * 100
                        bd = "Studio" if r.get('is_studio') == 1 else f"{int(r['bedrooms_clean'])} BR"
                        st.markdown(f"""
                        <div class="similar-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <b style="color:#6366f1;">#{i}</b>
                                    <b>{r['area_value']:.0f} sqm · {bd} · {int(r['bathrooms_clean'])} bath</b>
                                    <div style="color:#6b7280; font-size:0.9rem; margin-top:0.25rem;">
                                        📍 {r['city']} → {r['district']} · {sim:.0f}% match
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    <div style="font-size:1.4rem; font-weight:800; color:#10b981;">
                                        {r['predicted_price']/1e6:.2f}M
                                    </div>
                                    <div style="font-size:0.75rem; color:#9ca3af;">EGP</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

        with tab4:
            st.markdown("#### 💰 Investment ROI (5 Years)")
            roi = calculate_roi(price, years=5)
            c1, c2, c3, c4 = st.columns(4)
            metrics = [
                ("Total ROI", f"{roi['roi_pct']:.0f}%", "#6366f1"),
                ("Annualized", f"{roi['annualized_roi_pct']:.1f}%", "#10b981"),
                ("Rental (5y)", f"{roi['total_rental_income']/1e6:.2f}M", "#f59e0b"),
                ("Appreciation", f"{roi['appreciation_gain']/1e6:.2f}M", "#8b5cf6"),
            ]
            for col, (label, val, color) in zip([c1, c2, c3, c4], metrics):
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


st.markdown(f"""
<div class="footer-note">
    <b>Smart House Price Predictor</b> v6.0 · {metadata['model_name']} ·
    R2 {m['r2']:.4f} · MAPE {m['mape']:.2f}%
    <br><br>
    AI estimation tool — not a certified appraisal.
</div>
""", unsafe_allow_html=True)
