"""Smart House Price Predictor - Streamlit UI v5.0 (Bilingual, 8 Tabs)"""
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
    recommend_similar_properties, calculate_roi, compare_properties,
)
from sentiment_helper import analyze_sentiment

try:
    from pdf_report import generate_pdf_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from monitoring import (
        log_prediction, get_monitoring_stats, clear_log
    )
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

st.set_page_config(page_title="Smart House Price Predictor",
                   page_icon="🏠", layout="wide",
                   initial_sidebar_state="collapsed")


# ============================================================
# TRANSLATIONS
# ============================================================
T = {
    "en": {
        "title": "Smart House Price Predictor",
        "subtitle": "AI-powered property price prediction for the Egyptian real estate market",
        "property_details": "Property Details",
        "size_rooms": "Size & Rooms",
        "area": "Area (m²)", "bedrooms": "Bedrooms", "bathrooms": "Bathrooms",
        "location": "Location", "city": "City", "town": "Town",
        "district": "District", "subdistrict": "Subdistrict",
        "status": "Status & Features", "furnished": "Furnished",
        "completion": "Completion Status", "reception": "Reception",
        "living": "Living", "kitchen": "Kitchen",
        "description": "Property Description (Optional)",
        "desc_placeholder": "e.g., sea view furnished luxury apartment",
        "predict_btn": "Predict Property Price",
        "tab_pred": "Prediction", "tab_explain": "AI Explanation",
        "tab_map": "Price Map", "tab_whatif": "What-If",
        "tab_forecast": "Forecast", "tab_rec": "Recommendations",
        "tab_compare": "Comparison", "tab_roi": "ROI Calculator",
        "estimated": "Estimated Market Price", "confidence": "Confidence Range",
        "price_sqm": "Price per m²", "district_avg": "District Avg",
        "vs_district": "vs District Avg",
        "sentiment": "Description Sentiment",
        "download_pdf": "📄 Download PDF Report",
        "model_info": "Model Information",
        "disclaimer": "Educational AI tool — not a substitute for professional real estate appraisal.",
    },
    "ar": {
        "title": "🏠 متنبئ أسعار العقارات الذكي",
        "subtitle": "نظام ذكاء اصطناعي للتنبؤ بأسعار العقارات السكنية في مصر",
        "property_details": "تفاصيل العقار",
        "size_rooms": "المساحة والغرف",
        "area": "المساحة (م²)", "bedrooms": "غرف النوم", "bathrooms": "الحمامات",
        "location": "الموقع", "city": "المدينة", "town": "المنطقة",
        "district": "الحي", "subdistrict": "التقسيم",
        "status": "الحالة والمميزات", "furnished": "التأثيث",
        "completion": "حالة التشطيب", "reception": "صالة",
        "living": "معيشة", "kitchen": "مطبخ",
        "description": "وصف العقار (اختياري)",
        "desc_placeholder": "مثال: شقة بحرية مفروشة سوبر لوكس",
        "predict_btn": "🔮 توقع السعر",
        "tab_pred": "التوقع", "tab_explain": "تفسير AI",
        "tab_map": "خريطة الأسعار", "tab_whatif": "ماذا-لو",
        "tab_forecast": "التوقعات", "tab_rec": "عقارات مشابهة",
        "tab_compare": "مقارنة", "tab_roi": "حاسبة العائد",
        "estimated": "السعر المتوقع", "confidence": "نطاق الثقة",
        "price_sqm": "سعر المتر", "district_avg": "متوسط الحي",
        "vs_district": "مقارنة بمتوسط الحي",
        "sentiment": "تحليل الوصف",
        "download_pdf": "📄 تحميل تقرير PDF",
        "model_info": "معلومات النموذج",
        "disclaimer": "أداة تعليمية — لا تُغني عن التقييم الرسمي.",
    },
}


# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .main { padding: 0 2rem; }
    section[data-testid="stSidebar"] { display: none; }
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2.5rem 2rem; border-radius: 1.5rem; color: white;
        text-align: center; margin-bottom: 1.5rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.35);
    }
    .hero h1 { font-size: 2.8rem; font-weight: 900; margin: 0; }
    .hero p { font-size: 1.1rem; opacity: 0.95; margin-top: 0.5rem; }
    .hero-badges { display: flex; justify-content: center; gap: 0.8rem;
        margin-top: 1.2rem; flex-wrap: wrap; }
    .hero-badge { background: rgba(255,255,255,0.2); padding: 0.4rem 1rem;
        border-radius: 2rem; font-weight: 600; font-size: 0.85rem; }
    .card { background: white; border-radius: 1rem; padding: 1.25rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #f0f0f0;
        margin-bottom: 1rem; }
    .card-title { font-size: 1.05rem; font-weight: 700; color: #1a1a1a;
        margin-bottom: 0.85rem; padding-bottom: 0.6rem;
        border-bottom: 2px solid #f0f0f0; }
    .section-title { font-size: 1.35rem; font-weight: 800; color: #1a1a1a;
        margin: 1.5rem 0 0.85rem 0; }
    .price-card { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem; border-radius: 1.25rem; color: white;
        text-align: center; box-shadow: 0 15px 40px rgba(17, 153, 142, 0.3); }
    .price-label { font-size: 0.85rem; opacity: 0.9;
        text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
    .price-value { font-size: 3.5rem; font-weight: 900; margin: 0.5rem 0;
        line-height: 1; }
    .price-sub { font-size: 1.2rem; opacity: 0.95; }
    .price-range { margin-top: 1.25rem; padding-top: 1.25rem;
        border-top: 1px solid rgba(255,255,255,0.3); font-size: 0.9rem; }
    .stat-card { background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 0.75rem; padding: 1rem; text-align: center;
        border: 1px solid #e9ecef; }
    .stat-value { font-size: 1.6rem; font-weight: 800; color: #667eea;
        line-height: 1; }
    .stat-label { font-size: 0.8rem; color: #6c757d; margin-top: 0.4rem;
        font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .stButton > button { width: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white; font-weight: 700; padding: 0.85rem;
        border-radius: 0.75rem; border: none; font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    .stTabs [data-baseweb="tab-list"] { gap: 0.4rem; background: white;
        padding: 0.4rem; border-radius: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { border-radius: 0.6rem;
        padding: 0.6rem 1rem; font-weight: 600; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important; }
    .footer { text-align: center; color: #adb5bd; padding: 2rem 0;
        font-size: 0.85rem; border-top: 1px solid #e9ecef; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD
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
# LANGUAGE TOGGLE + HERO
# ============================================================
lang_col1, lang_col2 = st.columns([4, 1])
with lang_col2:
    lang = st.selectbox("🌐 Language", ["EN", "AR"], key="lang",
                        label_visibility="collapsed")
L = T["en"] if lang == "EN" else T["ar"]

st.markdown(f"""
<div class="hero">
    <h1>{L['title']}</h1>
    <p>{L['subtitle']}</p>
    <div class="hero-badges">
        <span class="hero-badge">R² {m['r2']:.4f}</span>
        <span class="hero-badge">MAPE {m['mape']:.2f}%</span>
        <span class="hero-badge">{metadata['features']['total']} Features</span>
        <span class="hero-badge">{metadata['training_info']['n_train']:,} samples</span>
    </div>
</div>
""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
s1.markdown(f'<div class="stat-card"><div class="stat-value">{m["r2"]:.4f}</div><div class="stat-label">R² Score</div></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="stat-card"><div class="stat-value">{m["mape"]:.2f}%</div><div class="stat-label">MAPE</div></div>', unsafe_allow_html=True)
s3.markdown(f'<div class="stat-card"><div class="stat-value">{m["mae"]/1000:,.0f}K</div><div class="stat-label">MAE (EGP)</div></div>', unsafe_allow_html=True)
s4.markdown(f'<div class="stat-card"><div class="stat-value">{metadata["features"]["total"]}</div><div class="stat-label">Features</div></div>', unsafe_allow_html=True)


# ============================================================
# INPUT FORM
# ============================================================
st.markdown(f'<div class="section-title">📝 {L["property_details"]}</div>',
            unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="card"><div class="card-title">📐 {L["size_rooms"]}</div>', unsafe_allow_html=True)
    area = st.slider(L["area"], 40, 500, 150, 5)
    bedrooms = st.selectbox(L["bedrooms"], ["studio","1","2","3","4","5","6"], index=3)
    bathrooms = st.slider(L["bathrooms"], 1, 5, 2)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="card"><div class="card-title">📍 {L["location"]}</div>', unsafe_allow_html=True)
    city = st.selectbox(L["city"], categories["city"])
    town = st.selectbox(L["town"], categories["town"])
    district = st.selectbox(L["district"], categories["district"])
    subdistrict = st.selectbox(L["subdistrict"], categories["subdistrict"])
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="card"><div class="card-title">🏗️ {L["status"]}</div>', unsafe_allow_html=True)
    furnished = st.selectbox(L["furnished"], categories["furnished"])
    completion_status = st.selectbox(L["completion"], categories["completion_status"])
    cc1, cc2, cc3 = st.columns(3)
    has_reception = cc1.checkbox(L["reception"], True)
    has_living = cc2.checkbox(L["living"], True)
    has_kitchen = cc3.checkbox(L["kitchen"], True)
    st.markdown('</div>', unsafe_allow_html=True)

description = st.text_area(L["description"], height=70,
                            placeholder=L["desc_placeholder"])
sentiment = analyze_sentiment(description) if description else None

st.markdown("<br>", unsafe_allow_html=True)
predict_btn = st.button(L["predict_btn"], type="primary", use_container_width=True)


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
# 8 TABS
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
tabs = st.tabs([
    f"🎯 {L['tab_pred']}", f"🔍 {L['tab_explain']}", f"🗺️ {L['tab_map']}",
    f"🎛️ {L['tab_whatif']}", f"📈 {L['tab_forecast']}",
    f"🏘️ {L['tab_rec']}", f"⚖️ {L['tab_compare']}", f"💰 {L['tab_roi']}",
    "📊 Monitoring", "🧠 Global Insights",
])


# ---------- Tab 1: Prediction ----------
with tabs[0]:
    if predict_btn:
        errors = validate_input(area, bedrooms, bathrooms, city, town,
                                 district, subdistrict, furnished, completion_status)
        if errors:
            st.error("⚠️ " + " | ".join(errors))
        else:
            result = predict_with_confidence(model, input_features, m["mape"])
            price = result["price"]
            ppm = price / area

            cc1, cc2 = st.columns([2, 1])
            with cc1:
                st.markdown(f"""
                <div class="price-card">
                    <div class="price-label">{L['estimated']}</div>
                    <div class="price-value">{price/1_000_000:.2f}M</div>
                    <div class="price-sub">{price:,.0f} EGP</div>
                    <div class="price-range">
                        📊 {L['confidence']}: {format_price(result['lower_bound'])} — {format_price(result['upper_bound'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Log this prediction for monitoring
                if MONITORING_AVAILABLE:
                    try:
                        log_prediction(
                            area=area, bedrooms=bedrooms, bathrooms=bathrooms,
                            city=city, town=town, district=district,
                            predicted_price=price,
                            confidence_lower=result['lower_bound'],
                            confidence_upper=result['upper_bound'],
                        )
                    except Exception:
                        pass

                if sentiment:
                    emoji = "😊" if sentiment['label'] == 'positive' else "😐" if sentiment['label'] == 'neutral' else "😟"
                    st.markdown(f"""
                    <div style="background:#f8f9fa;padding:0.85rem;border-radius:0.75rem;margin-top:0.75rem;border-left:4px solid {'#43A047' if sentiment['label']=='positive' else '#FB8C00' if sentiment['label']=='neutral' else '#E53935'}">
                        <b>{emoji} {L['sentiment']}:</b> {sentiment['label'].title()} ({sentiment['score']:+.2f})
                    </div>
                    """, unsafe_allow_html=True)

            with cc2:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{ppm:,.0f}</div><div class="stat-label">{L["price_sqm"]}</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                dist_avg = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
                diff = ppm - dist_avg
                diff_pct = (diff / dist_avg * 100) if dist_avg > 0 else 0
                st.markdown(f'<div class="stat-card"><div class="stat-value">{dist_avg:,.0f}</div><div class="stat-label">{L["district_avg"]}</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                col = "🟢" if diff >= 0 else "🔴"
                st.markdown(f'<div class="stat-card"><div class="stat-value">{col} {diff_pct:+.1f}%</div><div class="stat-label">{L["vs_district"]}</div></div>', unsafe_allow_html=True)

            # PDF Download
            if PDF_AVAILABLE:
                try:
                    property_data = {
                        'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
                        'city': city, 'town': town, 'district': district,
                        'subdistrict': subdistrict, 'furnished': furnished,
                        'completion_status': completion_status,
                    }
                    pred_data = {
                        'price': price,
                        'lower_bound': result['lower_bound'],
                        'upper_bound': result['upper_bound'],
                        'price_per_sqm': ppm,
                    }
                    meta_data = {
                        'model_name': metadata['model_name'],
                        'r2': m['r2'], 'mape': m['mape'],
                        'n_train': metadata['training_info']['n_train'],
                    }
                    pdf_buf = generate_pdf_report(pred_data, property_data, meta_data)
                    st.download_button(
                        L["download_pdf"],
                        data=pdf_buf,
                        file_name=f"property_report_{int(price)}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.warning(f"PDF unavailable: {e}")

            # Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=ppm,
                delta={"reference": dist_avg, "suffix": " EGP"},
                title={"text": f"{L['price_sqm']} vs {L['district_avg']}"},
                gauge={
                    "axis": {"range": [0, 80000]},
                    "bar": {"color": "#667eea"},
                    "steps": [
                        {"range": [0, 20000], "color": "#E8F5E9"},
                        {"range": [20000, 40000], "color": "#FFF9C4"},
                        {"range": [40000, 60000], "color": "#FFE0B2"},
                        {"range": [60000, 80000], "color": "#FFCDD2"},
                    ],
                    "threshold": {"line": {"color": "#e74c3c", "width": 3},
                                   "value": dist_avg},
                },
            ))
            fig.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Fill in the property details above and click **Predict**")


# ---------- Tab 2: SHAP ----------
with tabs[1]:
    st.markdown('<div class="section-title">🧠 SHAP Feature Contributions</div>', unsafe_allow_html=True)
    st.caption("Green = pushes price up · Red = pushes price down")

    @st.cache_resource
    def _shap(_model):
        return shap.TreeExplainer(_model.named_steps['model'])

    try:
        prep = model.named_steps['prep']
        X_t = prep.transform(input_features)
        feat_names = prep.get_feature_names_out()
        sv = _shap(model).shap_values(X_t)
        sv_flat = np.array(sv).flatten()
        top_n = 15
        idx = np.argsort(np.abs(sv_flat))[-top_n:][::-1]
        colors = ['#43A047' if v > 0 else '#E53935' for v in sv_flat[idx]]

        fig = go.Figure(go.Bar(
            x=sv_flat[idx],
            y=[feat_names[i].replace('num__','').replace('cat__','').replace('_',' ').title() for i in idx],
            orientation='h', marker_color=colors,
            text=[f"{v:+.3f}" for v in sv_flat[idx]], textposition='outside',
        ))
        fig.update_layout(title=f"Top {top_n} Contributions", height=550,
                          margin=dict(l=20, r=20, t=60, b=20),
                          xaxis_title="SHAP Value", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stat-card"><div class="stat-value">{int(np.sum(sv_flat>0))}</div><div class="stat-label">↑ Price</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-card"><div class="stat-value">{int(np.sum(sv_flat<0))}</div><div class="stat-label">↓ Price</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-card"><div class="stat-value">{len(sv_flat)}</div><div class="stat-label">Total</div></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"SHAP error: {e}")


# ---------- Tab 3: Map ----------
with tabs[2]:
    st.markdown('<div class="section-title">🗺️ Egypt Real Estate Price Map</div>', unsafe_allow_html=True)
    price_data = mappings["price_mappings"]["district_price_per_sqm"]
    city_centers = {
        "Cairo": (30.04, 31.24), "Giza": (30.01, 31.21),
        "Alexandria": (31.20, 29.92), "Mansoura": (31.04, 31.38),
        "Tanta": (30.79, 31.00), "Port Said": (31.27, 32.30),
        "Suez": (29.97, 32.55), "Ismailia": (30.60, 32.27),
        "Luxor": (25.69, 32.64), "Aswan": (24.09, 32.90),
    }

    m_map = folium.Map(location=[27, 31], zoom_start=6, tiles="cartodbpositron")
    for d_name, ppm_val in price_data.items():
        h = abs(hash(d_name))
        ck = list(city_centers.keys())[h % len(city_centers)]
        lat, lon = city_centers[ck]
        lat = lat + ((h // 7) % 60 - 30) / 500
        lon = lon + ((h // 13) % 60 - 30) / 500
        color = '#43A047' if ppm_val < 25000 else '#FB8C00' if ppm_val < 40000 else '#E53935'
        folium.CircleMarker([lat, lon], radius=8 + min(ppm_val/5000, 12),
                             color=color, fill=True, fill_opacity=0.75, weight=2,
                             popup=f"{d_name}: {ppm_val:,.0f} EGP/m2",
                             tooltip=f"{d_name}: {ppm_val:,.0f} EGP/m2").add_to(m_map)
    st_folium(m_map, width=None, height=500, returned_objects=[])

    ppm_series = pd.Series(price_data).sort_values(ascending=True)
    fig2 = go.Figure(go.Bar(
        x=ppm_series.values, y=ppm_series.index, orientation='h',
        marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
        text=[f"{v:,.0f}" for v in ppm_series.values], textposition='outside',
    ))
    fig2.update_layout(title="District Ranking by Price/m2", height=600,
                       margin=dict(l=20, r=60, t=60, b=20))
    st.plotly_chart(fig2, use_container_width=True)


# ---------- Tab 4: What-If ----------
with tabs[3]:
    st.markdown('<div class="section-title">What-If Scenario Analysis</div>', unsafe_allow_html=True)
    base_price = predict_price(model, input_features)

    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="stat-card"><div class="stat-value">{base_price/1_000_000:.2f}M</div><div class="stat-label">Base Price (EGP)</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        delta_area = st.slider("Delta Area (m2)", -100, 200, 0, 10)
    with col2:
        bd_base = 1 if bedrooms == "studio" else int(bedrooms)
        delta_bedrooms = st.slider("Delta Bedrooms", -3, 3, 0)

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
    pct = (diff / base_price * 100) if base_price > 0 else 0

    c2.markdown(f'<div class="stat-card"><div class="stat-value">{new_price/1_000_000:.2f}M</div><div class="stat-label">New Price (EGP)</div></div>', unsafe_allow_html=True)

    fig3 = go.Figure(go.Waterfall(
        x=["Base", "Delta Area", "Delta Bedrooms", "New"],
        measure=["absolute","relative","relative","total"],
        y=[base_price, (delta_area/100)*base_price*0.3, delta_bedrooms*base_price*0.05, new_price],
        text=[f"{base_price:,.0f}", f"{(delta_area/100)*base_price*0.3:+,.0f}",
              f"{delta_bedrooms*base_price*0.05:+,.0f}", f"{new_price:,.0f}"],
        connector={"line":{"color":"rgb(63,63,63)"}},
        decreasing={"marker":{"color":"#E53935"}},
        increasing={"marker":{"color":"#43A047"}},
        totals={"marker":{"color":"#667eea"}},
    ))
    fig3.update_layout(title="What-If Waterfall", height=400)
    st.plotly_chart(fig3, use_container_width=True)

    color = "#11998e, #38ef7d" if diff >= 0 else "#eb3349, #f45c43"
    st.markdown(f"""
    <div class="price-card" style="background: linear-gradient(135deg, {color});">
        <div class="price-label">New Price</div>
        <div class="price-value">{new_price/1_000_000:.2f}M</div>
        <div class="price-sub">{new_price:,.0f} EGP</div>
        <div class="price-range">Change: {'+' if diff>=0 else ''}{diff:,.0f} EGP ({pct:+.1f}%)</div>
    </div>""", unsafe_allow_html=True)


# ---------- Tab 5: Forecast ----------
with tabs[4]:
    st.markdown('<div class="section-title">12-Month Price Forecast by City</div>', unsafe_allow_html=True)
    try:
        import joblib as _jl
        ts_path = Path(__file__).resolve().parent / "models" / "time_series_forecasts.joblib"
        ts_data = _jl.load(ts_path)

        fig = go.Figure()
        colors = px.colors.qualitative.Set2
        for i, (city_name, data) in enumerate(ts_data.items()):
            hist = pd.DataFrame(data['historical'])
            fut = pd.DataFrame(data['forecast'])
            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=hist['ds'], y=hist['y'], mode='lines',
                name=f"{city_name} (hist)", line=dict(color=color, width=1.5),
            ))
            fig.add_trace(go.Scatter(
                x=fut['ds'], y=fut['yhat'], mode='lines',
                name=f"{city_name} (forecast)",
                line=dict(color=color, width=2.5, dash='dash'),
            ))
        fig.update_layout(title="Price per m2 - History + 12M Forecast",
                          height=500, xaxis_title="Date",
                          yaxis_title="EGP/m2", hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Expected Growth</div>', unsafe_allow_html=True)
        growth_data = []
        for cn, d in ts_data.items():
            growth_data.append({
                'City': cn,
                'Current (EGP/m2)': f"{d['current_price']:,.0f}",
                'Forecast +12M': f"{d['forecast_12m']:,.0f}",
                'Growth': f"{d['growth_12m_pct']:+.1f}%",
            })
        st.dataframe(pd.DataFrame(growth_data), hide_index=True, use_container_width=True)
    except Exception as e:
        st.error(f"Forecast error: {e}")


# ---------- Tab 6: Recommendations ----------
with tabs[5]:
    st.markdown('<div class="section-title">Similar Properties in the Dataset</div>', unsafe_allow_html=True)
    st.caption("Top 5 most similar properties based on cosine similarity of engineered features.")

    try:
        recs = recommend_similar_properties(
            area=area, bedrooms=bedrooms, bathrooms=bathrooms,
            city=city, town=town, district=district, subdistrict=subdistrict,
            furnished=furnished, completion_status=completion_status, top_n=5,
        )
        if recs:
            for i, r in enumerate(recs, 1):
                sim_pct = r['similarity'] * 100
                price_m = r['predicted_price'] / 1_000_000
                bd = "Studio" if r.get('is_studio') == 1 else f"{int(r['bedrooms_clean'])}BR"
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <h4 style="margin:0;">#{i} - {r['area_value']:.0f} m2 - {bd} - {int(r['bathrooms_clean'])} bath</h4>
                            <p style="color:#6c757d;margin:0.3rem 0;">
                                {r['city']} -> {r['town']} -> {r['district']} ({r['subdistrict']})
                            </p>
                            <p style="color:#6c757d;margin:0;">
                                Furnished: {r['furnished']} | Status: {r['completion_status']}
                            </p>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:1.5rem;font-weight:800;color:#11998e;">{price_m:.2f}M</div>
                            <div style="font-size:0.8rem;color:#6c757d;">EGP</div>
                            <div style="font-size:0.8rem;color:#667eea;margin-top:0.3rem;">
                                {sim_pct:.1f}% similar
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recommendations available.")
    except Exception as e:
        st.error(f"Recommendation error: {e}")


# ---------- Tab 7: Comparison ----------
with tabs[6]:
    st.markdown('<div class="section-title">Property Comparison</div>', unsafe_allow_html=True)
    st.caption("Compare two properties side by side and see which offers better value.")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### Property A")
        a_area = st.number_input("Area A (m2)", 40, 500, 120, key="a_area")
        a_bed = st.selectbox("Bedrooms A", ["1","2","3","4","5"], index=1, key="a_bed")
        a_bath = st.slider("Bathrooms A", 1, 5, 2, key="a_bath")
        a_district = st.selectbox("District A", categories["district"], key="a_dist")
        a_city = st.selectbox("City A", categories["city"], key="a_city")

    with colB:
        st.markdown("#### Property B")
        b_area = st.number_input("Area B (m2)", 40, 500, 180, key="b_area")
        b_bed = st.selectbox("Bedrooms B", ["1","2","3","4","5"], index=3, key="b_bed")
        b_bath = st.slider("Bathrooms B", 1, 5, 3, key="b_bath")
        b_district = st.selectbox("District B", categories["district"], key="b_dist")
        b_city = st.selectbox("City B", categories["city"], key="b_city")

    if st.button("Compare Properties", key="compare_btn"):
        prop_a = {'area': a_area, 'bedrooms': a_bed, 'bathrooms': a_bath,
                  'city': a_city, 'town': categories["town"][0],
                  'district': a_district, 'subdistrict': categories["subdistrict"][0],
                  'furnished': "No", 'completion_status': "completed"}
        prop_b = {'area': b_area, 'bedrooms': b_bed, 'bathrooms': b_bath,
                  'city': b_city, 'town': categories["town"][0],
                  'district': b_district, 'subdistrict': categories["subdistrict"][0],
                  'furnished': "No", 'completion_status': "completed"}

        try:
            comp = compare_properties(model, mappings, prop_a, prop_b)
            pa = comp['property_a']
            pb = comp['property_b']

            cmp_df = pd.DataFrame({
                'Metric': ['Area (m2)', 'Total Price (EGP)', 'Price per m2 (EGP)'],
                'Property A': [f"{a_area}", f"{pa['price']:,.0f}", f"{pa['price_per_sqm']:,.0f}"],
                'Property B': [f"{b_area}", f"{pb['price']:,.0f}", f"{pb['price_per_sqm']:,.0f}"],
            })
            st.dataframe(cmp_df, hide_index=True, use_container_width=True)

            cc1, cc2 = st.columns(2)
            cc1.success(f"Cheaper: Property {comp['cheaper']} (by {comp['price_diff']:,.0f} EGP)")
            cc2.info(f"Better Value (per m2): Property {comp['better_value']}")
        except Exception as e:
            st.error(f"Comparison error: {e}")


# ---------- Tab 8: ROI ----------
with tabs[7]:
    st.markdown('<div class="section-title">Investment ROI Calculator</div>', unsafe_allow_html=True)

    purchase = predict_price(model, input_features)
    st.markdown(f'<div class="stat-card"><div class="stat-value">{purchase/1_000_000:.2f}M</div><div class="stat-label">Estimated Purchase Price (EGP)</div></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        years = st.slider("Investment Horizon (years)", 1, 20, 5)
    with col2:
        rent_pct = st.slider("Monthly Rent (% of price)", 0.1, 1.5, 0.5, 0.05) / 100
    with col3:
        appreci = st.slider("Annual Appreciation (%)", 5, 25, 12, 1) / 100

    roi = calculate_roi(purchase, years=years,
                         monthly_rent_pct=rent_pct,
                         annual_appreciation=appreci)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><div class="stat-value">{roi["roi_pct"]:.0f}%</div><div class="stat-label">Total ROI</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-value">{roi["annualized_roi_pct"]:.1f}%</div><div class="stat-label">Annualized ROI</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-value">{roi["total_rental_income"]/1e6:.2f}M</div><div class="stat-label">Rental Income</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-value">{roi["appreciation_gain"]/1e6:.2f}M</div><div class="stat-label">Appreciation</div></div>', unsafe_allow_html=True)

    timeline = []
    for y in range(years + 1):
        fv = purchase * ((1 + appreci) ** y)
        ri = purchase * rent_pct * 12 * y
        timeline.append({'Year': y, 'Property Value': fv, 'Rental Income': ri})

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(x=[t['Year'] for t in timeline],
                              y=[t['Rental Income']/1e6 for t in timeline],
                              name='Rental Income', marker_color='#43A047'))
    fig_roi.add_trace(go.Bar(x=[t['Year'] for t in timeline],
                              y=[(t['Property Value']-purchase)/1e6 for t in timeline],
                              name='Appreciation', marker_color='#667eea'))
    fig_roi.update_layout(barmode='stack', title='Return Breakdown Over Time',
                          height=400, xaxis_title='Year', yaxis_title='Million EGP')
    st.plotly_chart(fig_roi, use_container_width=True)


# ---------- Tab 9: Monitoring ----------
with tabs[8]:
    st.markdown('<div class="section-title">📊 Model Monitoring Dashboard</div>', unsafe_allow_html=True)
    st.caption("Live tracking of all predictions made in this app session and across users.")

    if not MONITORING_AVAILABLE:
        st.warning("Monitoring module not available.")
    else:
        try:
            stats = get_monitoring_stats()

            if not stats.get("has_data"):
                st.info("No predictions logged yet. Make a prediction in the **Prediction** tab to see stats here.")
            else:
                # Top metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f'<div class="stat-card"><div class="stat-value">{stats["total_predictions"]}</div><div class="stat-label">Total Predictions</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="stat-card"><div class="stat-value">{stats["mean_price"]/1_000_000:.2f}M</div><div class="stat-label">Mean Price (EGP)</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="stat-card"><div class="stat-value">{stats["median_price"]/1_000_000:.2f}M</div><div class="stat-label">Median Price (EGP)</div></div>', unsafe_allow_html=True)
                c4.markdown(f'<div class="stat-card"><div class="stat-value">{stats["mean_area"]:.0f}</div><div class="stat-label">Mean Area (m²)</div></div>', unsafe_allow_html=True)

                # Drift status
                drift = stats.get("drift", {})
                status = drift.get("status", "unknown")
                if status == "healthy":
                    st.success(f"✅ Model Drift Status: **Healthy** (z-score = {drift.get('z_score', 0):.2f})")
                elif status == "warning":
                    st.warning(f"⚠️ Model Drift Warning (z-score = {drift.get('z_score', 0):.2f})")
                elif status == "drift_detected":
                    st.error(f"🚨 Drift Detected (z-score = {drift.get('z_score', 0):.2f})")
                else:
                    st.info("No baseline comparison available yet.")

                # Distribution charts
                col1, col2 = st.columns(2)
                with col1:
                    fig_h = go.Figure(go.Histogram(
                        x=[p/1_000_000 for p in stats["all_prices"]],
                        nbinsx=25, marker_color='#667eea',
                    ))
                    fig_h.update_layout(
                        title="Distribution of Predicted Prices",
                        xaxis_title="Price (Million EGP)",
                        yaxis_title="Frequency",
                        height=350, plot_bgcolor='white',
                    )
                    st.plotly_chart(fig_h, use_container_width=True)

                with col2:
                    city_dist = stats.get("city_distribution", {})
                    if city_dist:
                        cities = list(city_dist.keys())
                        counts = list(city_dist.values())
                        fig_c = go.Figure(go.Bar(
                            x=counts, y=cities, orientation='h',
                            marker_color='#43A047',
                            text=counts, textposition='outside',
                        ))
                        fig_c.update_layout(
                            title="Predictions by City",
                            xaxis_title="Count", height=350, plot_bgcolor='white',
                        )
                        st.plotly_chart(fig_c, use_container_width=True)

                # Recent predictions table
                st.markdown("### Recent Predictions")
                recent = stats.get("recent", [])
                if recent:
                    recent_df = pd.DataFrame([
                        {
                            'Time': p['timestamp'][11:19],
                            'Area (m²)': f"{p['area']:.0f}",
                            'City': p['city'],
                            'District': p['district'],
                            'Price (EGP)': f"{p['predicted_price']:,.0f}",
                        }
                        for p in recent
                    ])
                    st.dataframe(recent_df, hide_index=True, use_container_width=True)

                # Clear button
                if st.button("🗑️ Clear Monitoring Log", key="clear_mon"):
                    clear_log()
                    st.success("Monitoring log cleared!")
                    st.rerun()

        except Exception as e:
            st.error(f"Monitoring error: {e}")


# ---------- Tab 10: Global Insights ----------
with tabs[9]:
    st.markdown('<div class="section-title">🧠 Global Model Insights</div>', unsafe_allow_html=True)
    st.caption("Aggregated insights across the entire test set — not just a single prediction.")

    try:
        import joblib as _jl
        insights_path = Path(__file__).resolve().parent / "models" / "global_insights.joblib"

        if not insights_path.exists():
            st.warning("Insights not yet computed. Run `python global_insights.py`.")
        else:
            insights = _jl.load(insights_path)

            # --- Global SHAP ---
            st.markdown("### 🌟 Top 20 Features (Global SHAP)")
            st.caption("Average |SHAP| across a sample of 200 test properties.")

            shap_data = insights["global_shap"]
            fig_gshap = go.Figure(go.Bar(
                x=shap_data["mean_abs_shap"],
                y=[n.replace('num__','').replace('cat__','').replace('_',' ').title()
                   for n in shap_data["feature_names"]],
                orientation='h',
                marker=dict(
                    color=shap_data["mean_abs_shap"],
                    colorscale='Viridis', showscale=False,
                ),
                text=[f"{v:.4f}" for v in shap_data["mean_abs_shap"]],
                textposition='outside',
            ))
            fig_gshap.update_layout(
                height=600, margin=dict(l=20, r=80, t=40, b=20),
                xaxis_title="Mean |SHAP|", plot_bgcolor='white',
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_gshap, use_container_width=True)

            # --- Per-City Metrics ---
            st.markdown("### 🏙️ Per-City Model Performance")
            city_metrics = insights["city_metrics"]
            city_df = pd.DataFrame([
                {
                    'City': city,
                    'R²': f"{m['r2']:.4f}",
                    'MAPE': f"{m['mape']:.2f}%",
                    'MAE (EGP)': f"{m['mae']:,.0f}",
                    'Samples': m['n'],
                }
                for city, m in sorted(city_metrics.items(),
                                       key=lambda x: -x[1]['r2'])
            ])
            st.dataframe(city_df, hide_index=True, use_container_width=True)

            # R² per city chart
            fig_city = go.Figure(go.Bar(
                x=[c for c in city_metrics.keys()],
                y=[m['r2'] for m in city_metrics.values()],
                marker_color='#667eea',
                text=[f"{m['r2']:.3f}" for m in city_metrics.values()],
                textposition='outside',
            ))
            fig_city.update_layout(
                title="R² Score by City",
                height=400, plot_bgcolor='white',
                yaxis=dict(range=[0.9, 1.0]),
            )
            st.plotly_chart(fig_city, use_container_width=True)

            # --- Learning Curves ---
            st.markdown("### 📈 Learning Curves")
            st.caption("Model performance vs training set size — check for overfitting/underfitting.")

            lc = insights["learning_curves"]
            fig_lc = go.Figure()
            fig_lc.add_trace(go.Scatter(
                x=lc["sizes"], y=lc["train_r2"],
                mode='lines+markers', name='Training R²',
                line=dict(color='#43A047', width=3),
            ))
            fig_lc.add_trace(go.Scatter(
                x=lc["sizes"], y=lc["test_r2"],
                mode='lines+markers', name='Test R²',
                line=dict(color='#E53935', width=3),
            ))
            fig_lc.update_layout(
                title="Learning Curve — R² vs Training Size",
                xaxis_title="Training Samples",
                yaxis_title="R²",
                height=400, plot_bgcolor='white',
                hovermode='x unified',
            )
            st.plotly_chart(fig_lc, use_container_width=True)

            # --- Residuals ---
            st.markdown("### 📊 Residual Analysis")
            st.caption("Distribution of prediction errors on the test set.")

            res = insights["residuals"]
            y_true = np.array(res["y_true"]) / 1e6
            y_pred = np.array(res["y_pred"]) / 1e6

            fig_res = go.Figure()
            fig_res.add_trace(go.Scatter(
                x=y_pred, y=y_true,
                mode='markers', name='Predictions',
                marker=dict(color='#667eea', opacity=0.5, size=6),
            ))
            lims = [min(y_pred.min(), y_true.min()), max(y_pred.max(), y_true.max())]
            fig_res.add_trace(go.Scatter(
                x=lims, y=lims, mode='lines',
                name='Perfect Prediction',
                line=dict(color='#E53935', dash='dash', width=2),
            ))
            fig_res.update_layout(
                title="Actual vs Predicted Prices",
                xaxis_title="Predicted (Million EGP)",
                yaxis_title="Actual (Million EGP)",
                height=450, plot_bgcolor='white',
            )
            st.plotly_chart(fig_res, use_container_width=True)

            # Residual histogram
            fig_rh = go.Figure(go.Histogram(
                x=(np.array(res["residuals"]) / 1e6).tolist(),
                nbinsx=40, marker_color='#FB8C00',
            ))
            fig_rh.update_layout(
                title="Residual Distribution (Actual - Predicted)",
                xaxis_title="Residual (Million EGP)",
                yaxis_title="Frequency", height=350, plot_bgcolor='white',
            )
            st.plotly_chart(fig_rh, use_container_width=True)

    except Exception as e:
        st.error(f"Global insights error: {e}")
        import traceback
        st.code(traceback.format_exc())




# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="footer">
    <b>Smart House Price Predictor</b> v5.0 - {metadata['model_name']} -
    R2: {m['r2']:.4f} - MAPE: {m['mape']:.2f}% -
    Trained on {metadata['training_info']['n_train']:,} samples across {len(categories['city'])} cities
    <br><br>
    {L['disclaimer']}
</div>
""", unsafe_allow_html=True)
