"""
Egypt Real Estate AI — Modern App v13
Best of Property Finder + Bayut + Zillow + Aqarmap + Nawy
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import folium
from streamlit_folium import folium_static
from datetime import datetime
import io
import sys
import json

# Setup
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

# Modern theme
from modern_theme import get_css, get_theme, t, load_translations

# Model
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
    calculate_roi, recommend_similar_properties,
)

# PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Images
try:
    from mock_images import get_property_images
    IMAGES_OK = True
except ImportError:
    IMAGES_OK = False


# ═══════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Egypt Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "dark" not in st.session_state:
    st.session_state.dark = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "current_prediction" not in st.session_state:
    st.session_state.current_prediction = None
if "compare_list" not in st.session_state:
    st.session_state.compare_list = []

lang = st.session_state.lang
dark = st.session_state.dark
rtl = "rtl" if lang == "ar" else "ltr"


# ═══════════════════════════════════════════════════════
# APPLY CSS
# ═══════════════════════════════════════════════════════
st.markdown(get_css(dark=dark, lang=lang), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# LOAD MODEL & DATA
# ═══════════════════════════════════════════════════════
@st.cache_resource
def _load_model():
    return load_artifacts()

@st.cache_data
def _load_df():
    return pd.read_csv(BASE / "data" / "processed" / "FINAL_DATASET_v9.csv")

@st.cache_data
def _load_hierarchy():
    with open(BASE / "data" / "egypt_hierarchy.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    model, metadata, mappings = _load_model()
    df = _load_df()
    hierarchy = _load_hierarchy()
    LOADED = True
except Exception as e:
    LOADED = False
    st.error(f"⚠️ Error loading: {e}")


if not LOADED:
    st.stop()


# ═══════════════════════════════════════════════════════
# TRANSLATIONS HELPER
# ═══════════════════════════════════════════════════════
def tr(section, key):
    return t(section, key, lang)


# ═══════════════════════════════════════════════════════
# PDF GENERATOR
# ═══════════════════════════════════════════════════════
def generate_pdf(prop):
    if not PDF_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    c.setFillColorRGB(0.39, 0.4, 0.95)
    c.rect(0, h - 100, w, 100, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, h - 60, "Egypt Real Estate AI")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 85, "Property Valuation Report")

    c.setFillColorRGB(0, 0, 0)
    y = h - 150
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Property Details")
    y -= 30
    c.setFont("Helvetica", 11)

    details = [
        ("Type", prop.get("property_type", "N/A")),
        ("Governorate", prop.get("governorate", "N/A")),
        ("District", prop.get("district", "N/A")),
        ("Size", f"{prop.get('size', 0):.0f} m2"),
        ("Bedrooms", f"{prop.get('bedrooms', 0):.0f}"),
        ("Bathrooms", f"{prop.get('bathrooms', 0):.0f}"),
    ]
    for k, v in details:
        c.drawString(60, y, f"{k}: {v}")
        y -= 22

    y -= 20
    c.setFillColorRGB(0.95, 0.35, 0.4)
    c.rect(40, y - 80, w - 80, 80, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, y - 35, f"Estimated Price: {prop.get('price', 0):,.0f} EGP")
    c.setFont("Helvetica", 12)
    c.drawString(60, y - 60, f"Per m2: {prop.get('ppm2', 0):,.0f} EGP")

    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 9)
    c.drawString(40, 40, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buf.seek(0)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════
# NAVBAR
# ═══════════════════════════════════════════════════════
col_logo, col_space, col_lang, col_theme = st.columns([3, 4, 1, 1])

with col_logo:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0;">
        <span style="font-size:28px;">🏠</span>
        <span style="font-size:20px;font-weight:900;color:{get_theme(dark)['primary']};">
            {tr('navbar', 'brand')}
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_lang:
    label = "🌐 EN" if lang == "ar" else "🌐 AR"
    if st.button(label, key="lang_btn", use_container_width=True):
        st.session_state.lang = "en" if lang == "ar" else "ar"
        st.rerun()

with col_theme:
    theme_icon = "☀️" if dark else "🌙"
    if st.button(theme_icon, key="theme_btn", use_container_width=True):
        st.session_state.dark = not dark
        st.rerun()


# ═══════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════
metrics = metadata["metrics"]
training = metadata["training_info"]

n_gov = sum(1 for g in hierarchy["governorates"] if g["listings"] > 0)

st.markdown(f"""
<div class="hero">
    <div class="hero-badge">{tr('hero', 'badge')}</div>
    <h1 class="hero-title">{tr('hero', 'title')}</h1>
    <p class="hero-subtitle">{tr('hero', 'subtitle')}</p>
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{metrics['r2']:.4f}</div>
            <div class="stat-label">🎯 {tr('stats', 'accuracy')}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{metrics['mape']:.1f}%</div>
            <div class="stat-label">📊 {tr('stats', 'error')}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{n_gov}</div>
            <div class="stat-label">🏛️ {tr('stats', 'governorates')}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{training['n_total']:,}</div>
            <div class="stat-label">🏘️ {tr('stats', 'listings')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 " + tr('estimator', 'title').replace('🎯 ', ''),
    "📊 " + tr('market', 'title').replace('📊 ', ''),
    "🗺️ " + ("الخريطة" if lang == "ar" else "Map"),
    "🧮 " + tr('mortgage', 'title').replace('🧮 ', ''),
    "⚖️ " + tr('compare', 'title').replace('⚖️ ', ''),
    "❤️ " + tr('favorites', 'title').replace('❤️ ', ''),
])


# ═══════════════════════════════════════════════════════
# TAB 1: AI ESTIMATOR
# ═══════════════════════════════════════════════════════
with tab1:
    col_form, col_result = st.columns([5, 7], gap="large")
    
    with col_form:
        st.markdown(f"""
        <div class="section-header">
            <div class="section-icon">📝</div>
            <div>
                <h2 class="section-title">{tr('estimator', 'title').replace('🎯 ', '')}</h2>
                <div class="section-subtitle">{tr('estimator', 'subtitle')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**1️⃣ {tr('estimator', 'step1')}**")
        
        gov_options = [g for g in hierarchy["governorates"] if g["listings"] > 0]
        gov_names = [f"{g['ar']} ({g['listings']:,})" if lang == "ar" else f"{g['en']} ({g['listings']:,})" for g in gov_options]
        
        gov_idx = st.selectbox(
            tr('hero', 'governorate'),
            range(len(gov_options)),
            format_func=lambda i: gov_names[i],
            key="sel_gov",
        )
        selected_gov = gov_options[gov_idx]
        
        cities = selected_gov.get("cities", [])
        if cities:
            city_names = [c["ar"] if lang == "ar" else c["en"] for c in cities]
            city_idx = st.selectbox(
                tr('hero', 'city'),
                range(len(cities)),
                format_func=lambda i: f"{city_names[i]} ({cities[i]['listings']:,})",
                key="sel_city",
            )
            selected_city = cities[city_idx]
        else:
            selected_city = {"districts": [], "compounds": []}
            st.selectbox(tr('hero', 'city'), ["—"], key="sel_city_empty")
        
        districts = selected_city.get("districts", [])
        if districts:
            dist_names = [d["ar"] if lang == "ar" else d["en"] for d in districts]
            dist_idx = st.selectbox(
                tr('hero', 'district'),
                range(len(districts)),
                format_func=lambda i: f"{dist_names[i]} ({districts[i]['listings']:,})",
                key="sel_dist",
            )
            selected_district = districts[dist_idx]
        else:
            selected_district = {"en": "Unknown", "ar": "غير معروف"}
            st.selectbox(tr('hero', 'district'), ["—"], key="sel_dist_empty")
        
        compounds = selected_city.get("compounds", [])
        if compounds:
            comp_names = ["— " + ("لا يوجد" if lang == "ar" else "None") + " —"] + [c["ar"] if lang == "ar" else c["en"] for c in compounds]
            comp_idx = st.selectbox(
                "🏘️ " + ("كومبوند" if lang == "ar" else "Compound"),
                range(len(comp_names)),
                format_func=lambda i: comp_names[i],
                key="sel_comp",
            )
            selected_compound = compounds[comp_idx - 1] if comp_idx > 0 else {"en": "No Compound", "ar": "لا يوجد"}
        else:
            selected_compound = {"en": "No Compound", "ar": "لا يوجد"}
        
        st.markdown("---")
        st.markdown(f"**2️⃣ {tr('estimator', 'step2')}**")
        
        ptype_map = {
            "Apartment": ("شقة", "🏢"),
            "Villa": ("فيلا", "🏡"),
            "Townhouse": ("تاون هاوس", "🏘️"),
            "Duplex": ("دوبلكس", "🏢"),
            "Penthouse": ("بنتهاوس", "🌇"),
            "Twin House": ("توين هاوس", "🏠"),
            "iVilla": ("آي فيلا", "🏰"),
            "Hotel Apartment": ("شقة فندقية", "🏨"),
            "Chalet": ("شاليه", "🏖️"),
        }
        ptype_labels = [f"{v[1]} {v[0] if lang == 'ar' else k}" for k, v in ptype_map.items()]
        ptype_keys = list(ptype_map.keys())
        
        ptype_idx = st.selectbox(
            tr('hero', 'property_type'),
            range(len(ptype_keys)),
            format_func=lambda i: ptype_labels[i],
            key="sel_ptype",
        )
        selected_ptype = ptype_keys[ptype_idx]
        
        c1, c2 = st.columns(2)
        with c1:
            size = st.number_input(tr('estimator', 'size'), 30, 5000, 200, 10, key="inp_size")
            bathrooms = st.number_input(tr('estimator', 'bathrooms'), 1, 15, 2, key="inp_baths")
        with c2:
            bedrooms = st.number_input(tr('estimator', 'bedrooms'), 0, 15, 3, key="inp_beds")
            floor = st.number_input(
                "🏢 " + ("الطابق" if lang == "ar" else "Floor"),
                0, 50, 3, key="inp_floor"
            )
        
        st.markdown("---")
        st.markdown(f"**3️⃣ {tr('estimator', 'step3')}**")
        
        finish_options_ar = ["طوب أحمر", "نصف تشطيب", "تشطيب كامل", "سوبر لوكس"]
        finish_options_en = ["Core & Shell", "Semi Finished", "Finished", "Super Lux"]
        finish_vals = ["Core & Shell", "Semi Finished", "Finished", "Super Lux"]
        
        finishing = st.selectbox(
            tr('estimator', 'finishing'),
            finish_vals,
            format_func=lambda x: finish_options_ar[finish_vals.index(x)] if lang == "ar" else finish_options_en[finish_vals.index(x)],
            key="inp_finishing",
        )
        
        furnished = st.selectbox(
            tr('estimator', 'furnished'),
            ["Unfurnished", "PARTLY", "Furnished"],
            format_func=lambda x: {
                "Unfurnished": tr('estimator', 'furnished_no'),
                "PARTLY": tr('estimator', 'furnished_partly'),
                "Furnished": tr('estimator', 'furnished_yes'),
            }[x],
            key="inp_furnished",
        )
        
        amenity_count = st.slider(
            "✨ " + ("عدد الكماليات" if lang == "ar" else "Amenities Count"),
            0, 20, 5, key="inp_amenities"
        )
        
        st.markdown("---")
        st.markdown(f"**4️⃣ {tr('estimator', 'step4')}**")
        
        predict_btn = st.button(
            tr('estimator', 'calculate'),
            type="primary",
            use_container_width=True,
            key="predict_btn",
        )


    with col_result:
        if predict_btn:
            with st.spinner(tr('estimator', 'calculating')):
                sample = df[
                    (df["governorate"] == selected_gov["en"]) &
                    (df["district"] == selected_district["en"])
                ]
                lat = sample["latitude"].median() if len(sample) > 0 else 30.0444
                lon = sample["longitude"].median() if len(sample) > 0 else 31.2357
                
                input_data = {}
                for f in metadata["features"]:
                    if f in metadata["cat_features"]:
                        input_data[f] = "Unknown"
                    else:
                        input_data[f] = 0
                
                input_data.update({
                    "size": size,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "amenity_count": amenity_count,
                    "images_count": 10,
                    "latitude": lat,
                    "longitude": lon,
                    "property_type": selected_ptype,
                    "governorate": selected_gov["en"],
                    "district": selected_district["en"],
                    "compound": selected_compound["en"],
                    "completion_status": "completed",
                    "furnished": furnished,
                    "seller_type": "Broker",
                    "developer_name": "Unknown",
                    "view": "Unknown",
                    "finishing_type": finishing,
                    "payment_method": "Unknown",
                    "town": selected_gov["en"],
                    "area_per_room": size / max(bedrooms, 1),
                    "total_rooms": bedrooms + bathrooms,
                    "bed_bath_ratio": bedrooms / max(bathrooms, 1),
                    "amenity_per_room": amenity_count / max(bedrooms + bathrooms, 1),
                    "images_per_room": 10 / max(bedrooms + bathrooms, 1),
                    "lat_x_lon": lat * lon,
                    "distance_to_cairo": 0,
                    "distance_to_coast": 0,
                    "distance_cairo_sq": 0,
                    "is_coastal": 0,
                    "is_cairo_center": 0,
                    "is_high_end": 1 if selected_ptype in ["Villa", "Palace"] else 0,
                    "is_luxury": 1 if selected_ptype in ["Villa", "Penthouse", "Twin House"] else 0,
                    "is_compound": 0 if selected_compound["en"] == "No Compound" else 1,
                    "is_premium": 0,
                    "is_featured": 0,
                    "walk_score": 50,
                    "transit_score": 50,
                    "amenity_score": amenity_count / 20,
                    "floor_level": floor,
                    "year_built": 2024,
                    "has_premium_info": 0,
                })
                
                X = build_features(input_data, metadata["features"], metadata["cat_features"])
                result = predict_with_confidence(model, X, metadata["features"], metadata["cat_features"])
                price = result["price"]
                ppm2 = price / size
                
                st.session_state.current_prediction = {
                    "id": f"pred_{datetime.now().timestamp()}",
                    "governorate": selected_gov["en"],
                    "governorate_ar": selected_gov["ar"],
                    "district": selected_district["en"],
                    "district_ar": selected_district["ar"],
                    "compound": selected_compound["en"],
                    "property_type": selected_ptype,
                    "size": size,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "floor": floor,
                    "price": price,
                    "ppm2": ppm2,
                    "lat": lat,
                    "lon": lon,
                }
            
            st.markdown(f"""
            <div class="price-card">
                <div class="price-label">{tr('estimator', 'result_title')}</div>
                <div class="price-value">{price:,.0f}</div>
                <div class="price-currency">EGP</div>
                <div class="price-per-m2">💰 {tr('estimator', 'per_sqm')}: {ppm2:,.0f} EGP/m²</div>
            </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3 = st.columns(3)
            m1.metric(
                "📉 " + tr('estimator', 'result_range'),
                f"{result['price_low']/1e6:.1f}M-{result['price_high']/1e6:.1f}M"
            )
            m2.metric(
                "🎯 " + tr('estimator', 'confidence'),
                f"{result['confidence']*100:.0f}%"
            )
            
            market_median = df[
                (df["governorate"] == selected_gov["en"]) &
                (df["property_type"] == selected_ptype)
            ]["price"].median()
            
            if pd.notna(market_median):
                diff = ((price - market_median) / market_median) * 100
                if diff > 10:
                    label = f"⬆️ {tr('estimator', 'above_market')} {diff:.0f}%"
                elif diff < -10:
                    label = f"⬇️ {tr('estimator', 'below_market')} {abs(diff):.0f}%"
                else:
                    label = f"➡️ {tr('estimator', 'at_market')}"
                m3.metric("📊 " + tr('estimator', 'vs_market'), label)
            
            st.markdown("---")
            b1, b2, b3, b4 = st.columns(4)
            
            with b1:
                if st.button(tr('estimator', 'save'), use_container_width=True, key="save_pred"):
                    st.session_state.favorites.append(st.session_state.current_prediction)
                    st.success(tr('estimator', 'saved'))
            
            with b2:
                wa_text = f"Interested in {selected_ptype} in {selected_district['en']}, {size}m2"
                wa_url = f"https://wa.me/201001234567?text={wa_text}"
                st.markdown(
                    f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
                    f'<button style="width:100%;padding:10px;background:#25D366;'
                    f'color:white;border:none;border-radius:12px;font-weight:800;'
                    f'font-size:14px;cursor:pointer;">{tr("estimator", "whatsapp")}</button></a>',
                    unsafe_allow_html=True,
                )
            
            with b3:
                st.markdown(
                    '<a href="tel:+201001234567" style="text-decoration:none;">'
                    '<button style="width:100%;padding:10px;background:#6366F1;'
                    'color:white;border:none;border-radius:12px;font-weight:800;'
                    f'font-size:14px;cursor:pointer;">{tr("estimator", "call")}</button></a>',
                    unsafe_allow_html=True,
                )
            
            with b4:
                if PDF_AVAILABLE:
                    pdf_data = generate_pdf(st.session_state.current_prediction)
                    if pdf_data:
                        st.download_button(
                            tr('estimator', 'pdf'),
                            data=pdf_data,
                            file_name=f"property_{selected_district['en']}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="pdf_dl",
                        )
        else:
            st.markdown(f"""
            <div class="empty-state">
                <div class="empty-icon">🏠</div>
                <div class="empty-title">{tr('hero', 'title')}</div>
                <p style="max-width:400px;margin:16px auto;">
                    {tr('hero', 'subtitle')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            
            # ═══════════ PROPERTY IMAGES ═══════════
            if IMAGES_OK and 'price' in dir():
                st.markdown(f"""
                <div class="section-header">
                    <div class="section-icon">📸</div>
                    <div><h3 class="section-title">{"صور العقار" if lang == "ar" else "Property Images"}</h3></div>
                </div>
                """, unsafe_allow_html=True)
                
                imgs = get_property_images(st.session_state.current_prediction["id"], selected_ptype, 5)
                img_cols = st.columns(5)
                for i, u in enumerate(imgs):
                    with img_cols[i]:
                        st.image(u, use_container_width=True)
                
                # ═══════════ MAP + TIME SERIES ═══════════
                st.markdown(f"""
                <div class="section-header">
                    <div class="section-icon">📍</div>
                    <div><h3 class="section-title">{"الموقع والتوقعات" if lang == "ar" else "Location & Forecast"}</h3></div>
                </div>
                """, unsafe_allow_html=True)
                
                col_map, col_ts = st.columns([1, 1])
                
                with col_map:
                    m = folium.Map(location=[lat, lon], zoom_start=13, tiles="CartoDB positron")
                    folium.Marker(
                        [lat, lon],
                        popup=f"<b>{selected_ptype}</b><br>{price:,.0f} EGP",
                        icon=folium.Icon(color="red", icon="home", prefix="fa"),
                    ).add_to(m)
                    folium_static(m, width=500, height=320)
                
                with col_ts:
                    base_price = price
                    years_ts = ["2022", "2023", "2024", "2025", "2026", "2027", "2028"]
                    growth_rates = [0.75, 0.85, 0.95, 1.0, 1.08, 1.17, 1.27]
                    prices_ts = [base_price * r for r in growth_rates]
                    colors = ['#94A3B8', '#94A3B8', '#94A3B8', '#6366F1', '#10B981', '#10B981', '#10B981']
                    
                    fig = go.Figure(go.Bar(
                        x=years_ts, y=prices_ts,
                        marker_color=colors,
                        text=[f"{p/1e6:.1f}M" for p in prices_ts],
                        textposition="outside",
                    ))
                    fig.update_layout(
                        title=dict(text=tr('time_series', 'title'), font=dict(size=16)),
                        height=320,
                        margin=dict(l=20, r=20, t=50, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # ═══════════ SIMILAR PROPERTIES ═══════════
                st.markdown(f"""
                <div class="section-header">
                    <div class="section-icon">🏘️</div>
                    <div>
                        <h3 class="section-title">{tr('similar', 'title').replace('🏘️ ', '')}</h3>
                        <div class="section-subtitle">{tr('similar', 'subtitle')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                similar = df[
                    (df["governorate"] == selected_gov["en"]) &
                    (df["property_type"] == selected_ptype) &
                    (df["size"].between(size * 0.8, size * 1.2))
                ].head(3)
                
                if len(similar) > 0:
                    s_cols = st.columns(len(similar))
                    for i, (_, row) in enumerate(similar.iterrows()):
                        with s_cols[i]:
                            st.markdown(f"""
                            <div class="card">
                                <div class="card-value">{row['price']/1e6:.2f}M</div>
                                <div class="card-subtitle">
                                    {row['property_type']} · {row['district'][:25]}
                                </div>
                                <div style="margin-top:10px;font-size:13px;">
                                    📐 {row['size']:.0f}m² · 🛏️ {row['bedrooms']:.0f}BR · 🚿 {row['bathrooms']:.0f}BA
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("مفيش عقارات مشابهة" if lang == "ar" else "No similar properties")
                
                # ═══════════ ROI ANALYSIS ═══════════
                st.markdown(f"""
                <div class="section-header">
                    <div class="section-icon">📊</div>
                    <div><h3 class="section-title">{tr('roi', 'title').replace('📊 ', '')}</h3></div>
                </div>
                """, unsafe_allow_html=True)
                
                roi = calculate_roi(price, years=5, growth_rate=0.08)
                annual_rent = price * 0.07
                rental_yield = 7.0
                
                r1, r2, r3 = st.columns(3)
                r1.metric("💰 " + tr('roi', 'current_value'), f"{roi['current_price']/1e6:.2f}M")
                r2.metric("🏠 " + tr('roi', 'annual_rental'), f"{annual_rent/1e3:.0f}K")
                r3.metric("📈 " + tr('roi', 'rental_yield'), f"{rental_yield:.1f}%")
                
                r4, r5, r6 = st.columns(3)
                r4.metric("📅 " + tr('roi', '5yr_value'), f"{roi['future_price']/1e6:.2f}M")
                r5.metric("📊 " + tr('roi', 'appreciation'), f"+{roi['roi_percent']:.1f}%")
                r6.metric("🎯 " + tr('roi', 'total_roi'), f"{roi['roi_percent'] + rental_yield*5:.0f}%")


# ═══════════════════════════════════════════════════════
# TAB 2: MARKET
# ═══════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">📊</div>
        <div>
            <h2 class="section-title">{tr('market', 'title').replace('📈 ', '')}</h2>
            <div class="section-subtitle">{tr('market', 'subtitle')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📊 {tr('stats', 'listings')}</div>
            <div class="card-value">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">💰 {tr('market', 'median')}</div>
            <div class="card-value">{df['price'].median()/1e6:.1f}M</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📐 {tr('market', 'size') if 'size' in tr('market', 'size') else 'Size'}</div>
            <div class="card-value">{df['size'].median():.0f}m²</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🏙️ {tr('stats', 'districts')}</div>
            <div class="card-value">{df['district'].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(
            df, names='property_type', hole=0.5,
            title='🏢 ' + tr('market', 'by_type'),
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        avg = df.groupby('governorate')['price'].median().sort_values()
        fig = px.bar(
            x=avg.values, y=avg.index, orientation='h',
            title='💰 ' + tr('market', 'by_governorate'),
            color=avg.values, color_continuous_scale='Viridis',
        )
        fig.update_layout(height=420, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(
            df.sample(min(5000, len(df))), x='price', nbins=50,
            title='📊 ' + tr('market', 'price_distribution'),
            color_discrete_sequence=['#6366F1'],
        )
        fig.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with c4:
        sample = df.sample(min(2000, len(df)))
        fig = px.scatter(
            sample, x='size', y='price', color='property_type',
            title='📐 ' + tr('market', 'size_vs_price'), opacity=0.6,
        )
        fig.update_layout(height=420, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown(f"### 📋 {'جدول تفصيلي' if lang == 'ar' else 'Detailed Table'}")
    
    table = df.groupby('governorate').agg({
        'price': ['count', 'median', 'mean', 'min', 'max'],
        'size': 'median',
        'district': 'nunique',
        'compound': 'nunique',
    }).round(0)
    
    if lang == 'ar':
        table.columns = ['إعلانات', 'الوسيط', 'المتوسط', 'أقل', 'أعلى', 'المساحة', 'مناطق', 'كومبوندات']
    else:
        table.columns = ['Listings', 'Median', 'Mean', 'Min', 'Max', 'Size', 'Districts', 'Compounds']
    
    st.dataframe(table, use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 3: MAP + NEIGHBORHOOD
# ═══════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">🗺️</div>
        <div>
            <h2 class="section-title">{"الخريطة التفاعلية" if lang == "ar" else "Interactive Map"}</h2>
            <div class="section-subtitle">{"استكشف العقارات على الخريطة" if lang == "ar" else "Explore properties on the map"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        map_gov = st.selectbox("🏙️ " + tr('hero', 'governorate'), df['governorate'].unique(), key='map_g')
    with m2:
        map_type = st.selectbox("🏢 " + tr('hero', 'property_type'), ['All'] + list(df['property_type'].unique()), key='map_t')
    with m3:
        max_pts = st.slider("📍 Points", 100, 2000, 500, key='map_p')
    with m4:
        map_view = st.selectbox("👁️ View", ["Normal", "🔥 Heatmap"], key='map_v')
    
    filtered = df[df['governorate'] == map_gov]
    if map_type != 'All':
        filtered = filtered[filtered['property_type'] == map_type]
    
    sample = filtered.sample(min(max_pts, len(filtered))) if len(filtered) > 0 else filtered
    
    if len(sample) > 0:
        center_lat = sample['latitude'].median()
        center_lon = sample['longitude'].median()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='CartoDB positron')
        
        if map_view == '🔥 Heatmap':
            try:
                from folium.plugins import HeatMap
                hd = [[r['latitude'], r['longitude'], min(r['price'] / 1e7, 1)] for _, r in sample.iterrows()]
                HeatMap(hd, radius=15, blur=20).add_to(m)
            except:
                st.warning("Heatmap unavailable")
        else:
            median_price = sample['price'].median()
            for _, row in sample.iterrows():
                color = 'red' if row['price'] > median_price else 'blue'
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    popup=f"<b>{row['property_type']}</b><br>💰 {row['price']:,.0f} EGP<br>📐 {row['size']:.0f} m²",
                    color=color, fill=True, fillOpacity=0.6,
                ).add_to(m)
        
        folium_static(m, width=1300, height=500)
        
        st.markdown(f"""
        <div class="card" style="margin-top:16px;">
            <b>📊 {tr('market', 'listings_count')}:</b> {len(sample)} | 
            🔴 {'Above median' if lang == 'en' else 'أعلى من الوسيط'} | 
            🔵 {'Below median' if lang == 'en' else 'أقل من الوسيط'}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ═══════════ NEIGHBORHOOD INSIGHTS ═══════════
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">🏘️</div>
        <div>
            <h2 class="section-title">{tr('neighborhood', 'title').replace('🏘️ ', '')}</h2>
            <div class="section-subtitle">{tr('neighborhood', 'subtitle')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    n_dist = st.selectbox(
        "📍 " + tr('hero', 'district'),
        sorted(df['district'].unique())[:100],
        key='nb_dist'
    )
    
    if n_dist:
        n_df = df[df['district'] == n_dist]
        
        n1, n2, n3, n4 = st.columns(4)
        n1.metric("💰 " + tr('market', 'median'), f"{n_df['price'].median()/1e6:.1f}M")
        n2.metric("📐 " + tr('market', 'size'), f"{n_df['size'].median():.0f}m²")
        n3.metric("🏢 " + tr('stats', 'listings'), f"{len(n_df):,}")
        n4.metric("🏘️ " + tr('stats', 'compounds'), f"{n_df['compound'].nunique()}")
        
        # Amenities in neighborhood
        n_items = [
            ("🏫", tr('neighborhood', 'schools'), 12, 4.2),
            ("🏥", tr('neighborhood', 'hospitals'), 8, 4.5),
            ("🛍️", tr('neighborhood', 'malls'), 6, 4.7),
            ("🍽️", tr('neighborhood', 'restaurants'), 25, 4.3),
            ("🚌", tr('neighborhood', 'transport'), 15, 3.8),
            ("🌳", tr('neighborhood', 'parks'), 4, 4.0),
        ]
        
        n_cols = st.columns(3)
        for i, (icon, name, count, rating) in enumerate(n_items):
            with n_cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                    <div style="font-size:32px;">{icon}</div>
                    <div class="card-title">{name}</div>
                    <div class="card-value">{count}</div>
                    <div class="card-subtitle">⭐ {rating}</div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 4: MORTGAGE CALCULATOR
# ═══════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">🧮</div>
        <div>
            <h2 class="section-title">{tr('mortgage', 'title').replace('🧮 ', '')}</h2>
            <div class="section-subtitle">{tr('mortgage', 'subtitle')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    mc1, mc2 = st.columns([1, 1], gap="large")
    
    with mc1:
        st.markdown(f"**{'البيانات' if lang == 'ar' else 'Details'}**")
        
        p_price = st.number_input(
            "💰 " + tr('mortgage', 'property_price'),
            min_value=100_000, max_value=200_000_000,
            value=5_000_000, step=100_000,
            key="mort_price",
        )
        
        down_pct = st.slider(
            "📊 " + tr('mortgage', 'down_payment_pct'),
            min_value=5, max_value=50, value=20,
            key="mort_down",
        )
        
        years = st.slider(
            "📅 " + tr('mortgage', 'years'),
            min_value=5, max_value=30, value=20,
            key="mort_years",
        )
        
        rate = st.slider(
            "📈 " + tr('mortgage', 'interest_rate'),
            min_value=5.0, max_value=30.0, value=15.0, step=0.5,
            key="mort_rate",
        )
    
    with mc2:
        # الحسابات
        down_payment = p_price * down_pct / 100
        loan = p_price - down_payment
        mr = (rate / 100) / 12
        n = years * 12
        
        if mr > 0:
            monthly = loan * (mr * (1 + mr) ** n) / ((1 + mr) ** n - 1)
        else:
            monthly = loan / n
        
        total = monthly * n
        interest = total - loan
        
        st.markdown(f"""
        <div class="price-card">
            <div class="price-label">{tr('mortgage', 'monthly_payment')}</div>
            <div class="price-value">{monthly:,.0f}</div>
            <div class="price-currency">EGP / {'شهر' if lang == 'ar' else 'month'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        k1, k2 = st.columns(2)
        with k1:
            st.metric("💰 " + tr('mortgage', 'down_payment'), f"{down_payment:,.0f}")
            st.metric("📊 " + tr('mortgage', 'total_interest'), f"{interest:,.0f}")
        with k2:
            st.metric("🏦 " + tr('mortgage', 'loan_amount'), f"{loan:,.0f}")
            st.metric("💸 " + tr('mortgage', 'total_paid'), f"{total:,.0f}")
    
    st.markdown("---")
    
    # Schedule Table
    st.markdown(f"### 📅 {tr('mortgage', 'schedule')}")
    
    schedule = []
    bal = loan
    for month in range(1, min(13, n + 1)):
        i = bal * mr
        p = monthly - i
        bal -= p
        schedule.append({
            tr('mortgage', 'month'): month,
            tr('mortgage', 'payment'): f"{monthly:,.0f}",
            tr('mortgage', 'interest'): f"{i:,.0f}",
            tr('mortgage', 'principal'): f"{p:,.0f}",
            tr('mortgage', 'balance'): f"{max(0, bal):,.0f}",
        })
    
    st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)
    
    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[
            tr('mortgage', 'down_payment'),
            tr('mortgage', 'loan_amount'),
            tr('mortgage', 'total_interest'),
        ],
        values=[down_payment, loan, interest],
        hole=0.4,
        marker=dict(colors=['#6366F1', '#8B5CF6', '#EC4899']),
    )])
    fig.update_layout(
        title=dict(text='📊 ' + ('توزيع التكاليف' if lang == 'ar' else 'Cost Breakdown')),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 5: COMPARE
# ═══════════════════════════════════════════════════════
with tab5:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">⚖️</div>
        <div>
            <h2 class="section-title">{tr('compare', 'title').replace('⚖️ ', '')}</h2>
            <div class="section-subtitle">{tr('compare', 'subtitle')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    cc1, cc2 = st.columns(2)
    with cc1:
        comp_gov = st.selectbox("🏙️ " + tr('hero', 'governorate'), ['All'] + list(df['governorate'].unique()), key='comp_g')
    with cc2:
        comp_type = st.selectbox("🏢 " + tr('hero', 'property_type'), ['All'] + list(df['property_type'].unique()), key='comp_t')
    
    comp_df = df.copy()
    if comp_gov != 'All':
        comp_df = comp_df[comp_df['governorate'] == comp_gov]
    if comp_type != 'All':
        comp_df = comp_df[comp_df['property_type'] == comp_type]
    
    comp_sample = comp_df.sample(min(20, len(comp_df))) if len(comp_df) > 0 else comp_df
    
    if len(comp_sample) > 0:
        options = [
            f"{i+1}. {row['property_type']} - {row['district'][:20]} - {row['price']:,.0f} - {row['size']:.0f}m²"
            for i, (_, row) in enumerate(comp_sample.iterrows())
        ]
        
        selected = st.multiselect(
            "🎯 " + tr('compare', 'select'),
            options,
            max_selections=4,
            key='comp_select',
        )
        
        if len(selected) >= 2:
            selected_rows = []
            for sel in selected:
                idx = int(sel.split('.')[0]) - 1
                selected_rows.append(comp_sample.iloc[idx])
            
            comp_data = {
                tr('compare', 'property'): [f"#{i+1}" for i in range(len(selected_rows))],
                tr('compare', 'type'): [r['property_type'] for r in selected_rows],
                tr('compare', 'location'): [r['district'][:25] for r in selected_rows],
                tr('compare', 'price'): [f"{r['price']:,.0f}" for r in selected_rows],
                tr('compare', 'size'): [f"{r['size']:.0f}" for r in selected_rows],
                tr('compare', 'price_per_m2'): [f"{r['price']/r['size']:,.0f}" for r in selected_rows],
                tr('compare', 'bedrooms'): [f"{r['bedrooms']:.0f}" for r in selected_rows],
                tr('compare', 'bathrooms'): [f"{r['bathrooms']:.0f}" for r in selected_rows],
            }
            
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"#{i+1}" for i in range(len(selected_rows))],
                y=[r['price'] for r in selected_rows],
                marker_color=['#6366F1', '#8B5CF6', '#EC4899', '#10B981'][:len(selected_rows)],
                text=[f"{r['price']:,.0f}" for r in selected_rows],
                textposition='auto',
            ))
            fig.update_layout(
                title='💰 ' + tr('compare', 'price'),
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎯 " + ("اختار عقارين على الأقل" if lang == "ar" else "Select at least 2 properties"))


# ═══════════════════════════════════════════════════════
# TAB 6: FAVORITES
# ═══════════════════════════════════════════════════════
with tab6:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon">❤️</div>
        <div>
            <h2 class="section-title">{tr('favorites', 'title').replace('❤️ ', '')}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    favs = st.session_state.favorites
    
    if len(favs) == 0:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">💔</div>
            <div class="empty-title">{tr('favorites', 'empty')}</div>
            <p>{tr('favorites', 'empty_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### {'عندك' if lang == 'ar' else 'You have'} **{len(favs)}** {'عقار' if lang == 'ar' else 'properties'}")
        
        for i, fav in enumerate(favs):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-value">{fav['price']:,.0f} EGP</div>
                    <div class="card-subtitle">
                        {fav['property_type']} · 
                        {fav.get('district_ar', fav['district']) if lang == 'ar' else fav['district']}
                    </div>
                    <div style="margin-top:8px;font-size:13px;color:{get_theme(dark)['text_muted']};">
                        🏙️ {fav.get('governorate_ar', fav['governorate']) if lang == 'ar' else fav['governorate']} · 
                        📐 {fav['size']:.0f}m² · 
                        🛏️ {fav['bedrooms']:.0f}BR · 
                        🚿 {fav['bathrooms']:.0f}BA
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                    st.session_state.favorites.pop(i)
                    st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ " + tr('favorites', 'clear_all'), use_container_width=True):
            st.session_state.favorites = []
            st.rerun()


# ═══════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════
st.markdown(f"""
<div class="footer">
    <h3 style="margin:0 0 12px 0;font-size:20px;color:{get_theme(dark)['primary']};">
        🏠 {tr('navbar', 'brand').replace('🏠 ', '')}
    </h3>
    <p style="margin:8px 0;font-weight:600;">{tr('footer', 'made_with')}</p>
    <p style="margin:8px 0;font-size:13px;">
        {len(df):,} {tr('stats', 'listings')} · 
        {df['governorate'].nunique()} {tr('stats', 'governorates')} · 
        R² = {metadata['metrics']['r2']:.4f}
    </p>
    <p style="margin:16px 0 0 0;font-size:12px;opacity:0.7;">
        {tr('footer', 'copyright')}
    </p>
</div>
""", unsafe_allow_html=True)
