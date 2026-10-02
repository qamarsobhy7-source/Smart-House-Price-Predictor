"""
Egypt Real Estate AI - Modern App v11
Modern design with dark/light mode and language switcher
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

# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(
    page_title="Egypt Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# TRANSLATIONS
# ================================================================
TRANSLATIONS = {
    "ar": {
        "title": "🏠 الذكاء العقاري المصري",
        "subtitle": "🤖 توقع ذكي لأسعار العقارات في مصر",
        "stats": "📊 119,916 إعلان | 🏙️ 6 محافظات | 🎯 R² = 0.71",
        "tab_predict": "🎯 التوقع",
        "tab_market": "📊 تحليل السوق",
        "tab_map": "🗺️ الخريطة",
        "tab_mortgage": "🧮 حاسبة الرهن",
        "tab_compare": "⚖️ مقارنة",
        "tab_favorites": "❤️ المفضلة",
        "tab_about": "ℹ️ عن المشروع",
        "prop_specs": "📝 مواصفات العقار",
        "governorate": "🏙️ المحافظة",
        "district": "📍 المنطقة",
        "prop_type": "🏢 نوع العقار",
        "size": "📐 المساحة (م²)",
        "bedrooms": "🛏️ غرف",
        "bathrooms": "🚿 حمامات",
        "amenities": "✨ كماليات",
        "completion": "🏗️ حالة الإنشاء",
        "furnished": "🛋️ الفرش",
        "images": "📸 عدد الصور",
        "predict_btn": "🔮 توقع السعر",
        "estimated_price": "💰 السعر المتوقع",
        "price_per_m2": "💵 سعر المتر",
        "market_avg": "📊 متوسط السوق",
        "difference": "📈 الفرق",
        "save": "❤️ حفظ",
        "whatsapp": "📱 WhatsApp",
        "call": "📞 اتصل",
        "pdf": "📄 PDF",
        "images_section": "📸 صور العقار",
        "location": "📍 الموقع",
        "similar": "🏘️ عقارات مشابهة",
        "empty_prompt": "احسب سعر عقارك الآن",
        "empty_desc": "ادخل المواصفات واضغط توقع السعر",
    },
    "en": {
        "title": "🏠 Egypt Real Estate AI",
        "subtitle": "🤖 Smart Property Price Prediction",
        "stats": "📊 119,916 listings | 🏙️ 6 governorates | 🎯 R² = 0.71",
        "tab_predict": "🎯 Predict",
        "tab_market": "📊 Market",
        "tab_map": "🗺️ Map",
        "tab_mortgage": "🧮 Mortgage",
        "tab_compare": "⚖️ Compare",
        "tab_favorites": "❤️ Favorites",
        "tab_about": "ℹ️ About",
        "prop_specs": "📝 Property Specs",
        "governorate": "🏙️ Governorate",
        "district": "📍 District",
        "prop_type": "🏢 Property Type",
        "size": "📐 Size (m²)",
        "bedrooms": "🛏️ Bedrooms",
        "bathrooms": "🚿 Bathrooms",
        "amenities": "✨ Amenities",
        "completion": "🏗️ Completion",
        "furnished": "🛋️ Furnished",
        "images": "📸 Images",
        "predict_btn": "🔮 Predict Price",
        "estimated_price": "💰 Estimated Price",
        "price_per_m2": "💵 Price per m²",
        "market_avg": "📊 Market Avg",
        "difference": "📈 Difference",
        "save": "❤️ Save",
        "whatsapp": "📱 WhatsApp",
        "call": "📞 Call",
        "pdf": "📄 PDF",
        "images_section": "📸 Property Images",
        "location": "📍 Location",
        "similar": "🏘️ Similar Properties",
        "empty_prompt": "Calculate your property price",
        "empty_desc": "Enter specs and click Predict",
    },
}

# ================================================================
# INIT SESSION
# ================================================================
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "current_prediction" not in st.session_state:
    st.session_state.current_prediction = None
if "compare_list" not in st.session_state:
    st.session_state.compare_list = []

L = TRANSLATIONS[st.session_state.lang]
is_dark = st.session_state.theme == "dark"

# ================================================================
# MODERN CSS
# ================================================================
if is_dark:
    bg = "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
    card_bg = "#2d3748"
    text_color = "#f7fafc"
    muted_color = "#a0aec0"
    border = "#4a5568"
else:
    bg = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    card_bg = "#ffffff"
    text_color = "#1a202c"
    muted_color = "#718096"
    border = "#e2e8f0"

st.markdown(f"""
<style>
    .stApp {{
        background: {bg};
        color: {text_color};
    }}
    
    /* Hero Header */
    .hero {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.35);
        position: relative;
        overflow: hidden;
    }}
    .hero::before {{
        content: "";
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.5; }}
        50% {{ transform: scale(1.1); opacity: 0.8; }}
    }}
    .hero h1 {{
        margin: 0;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }}
    .hero p {{
        margin: 0.75rem 0 0 0;
        opacity: 0.95;
        font-size: 1.15rem;
        position: relative;
        z-index: 1;
    }}
    .hero .stats {{
        display: inline-block;
        margin-top: 1rem;
        background: rgba(255,255,255,0.15);
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        backdrop-filter: blur(10px);
        font-size: 0.95rem;
        position: relative;
        z-index: 1;
    }}
    
    /* Cards */
    .card {{
        background: {card_bg};
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid {border};
        transition: all 0.3s;
    }}
    .card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }}
    .card-title {{
        color: {muted_color};
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
        font-weight: 600;
    }}
    .card-value {{
        color: {text_color};
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }}
    
    /* Result Card */
    .result-card {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2.5rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 20px 60px rgba(245, 87, 108, 0.35);
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }}
    .result-card .label {{
        font-size: 1.1rem;
        opacity: 0.9;
        letter-spacing: 1px;
    }}
    .result-card .price {{
        font-size: 3.8rem;
        font-weight: 900;
        margin: 1rem 0;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.2);
        line-height: 1;
    }}
    .result-card .currency {{
        font-size: 1.3rem;
        opacity: 0.95;
    }}
    .result-card .ppm2 {{
        background: rgba(255,255,255,0.2);
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        display: inline-block;
        margin-top: 1rem;
        font-size: 1rem;
        backdrop-filter: blur(10px);
    }}
    
    /* Section Header */
    .section-header {{
        font-size: 1.6rem;
        font-weight: 800;
        color: {text_color};
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 4px solid #667eea;
        display: inline-block;
    }}
    
    /* Info Badge */
    .badge {{
        display: inline-block;
        padding: 0.4rem 0.9rem;
        background: rgba(102, 126, 234, 0.15);
        color: #667eea;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }}
    
    /* Property Card */
    .prop-card {{
        background: {card_bg};
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s;
        margin-bottom: 1rem;
        border: 1px solid {border};
    }}
    .prop-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(102, 126, 234, 0.25);
    }}
    .prop-card-body {{
        padding: 1rem;
    }}
    .prop-price {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #667eea;
        margin: 0;
    }}
    .prop-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {text_color};
        margin: 0.5rem 0;
    }}
    .prop-meta {{
        color: {muted_color};
        font-size: 0.85rem;
        margin: 0.25rem 0;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid {border};
        background: {card_bg};
        color: {text_color};
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: {card_bg};
        padding: 8px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid {border};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: 700;
        color: {text_color};
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {text_color};
        font-weight: 800;
    }}
    
    /* Empty state */
    .empty {{
        text-align: center;
        padding: 4rem 2rem;
        color: {muted_color};
    }}
    .empty-icon {{
        font-size: 5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }}
    .empty-title {{
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        color: {muted_color};
        padding: 2rem 0 1rem 0;
        margin-top: 3rem;
        border-top: 1px solid {border};
    }}
</style>
""", unsafe_allow_html=True)

print("✅ Part 1: Modern CSS اتحفظ")
print(f"📊 الملف: {app_file}")


# ================================================================
# LOAD MODEL & DATA
# ================================================================
@st.cache_resource
def load_model():
    base = Path(__file__).resolve().parent
    model = joblib.load(base / "models" / "FINAL_MODEL_v9.pkl")
    features = joblib.load(base / "models" / "FINAL_FEATURES_v9.pkl")
    cat_features = joblib.load(base / "models" / "FINAL_CAT_FEATURES_v9.pkl")
    return model, features, cat_features

@st.cache_data
def load_data():
    base = Path(__file__).resolve().parent
    return pd.read_csv(base / "data" / "processed" / "FINAL_DATASET_v9.csv")

# Custom modules
try:
    from mock_images import get_property_images
    CUSTOM_MODULES = True
except ImportError:
    CUSTOM_MODULES = False

try:
    model, features, cat_features = load_model()
    df = load_data()
    loaded = True
except Exception as e:
    loaded = False
    st.error(f"⚠️ Error loading: {e}")

# PDF function
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def generate_property_pdf(prop_data):
    """Generate a PDF report."""
    if not PDF_AVAILABLE:
        return None
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Header
    c.setFillColorRGB(0.4, 0.5, 0.9)
    c.rect(0, h - 100, w, 100, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, h - 60, "Egypt Real Estate AI")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 85, "Property Valuation Report")

    # Body
    c.setFillColorRGB(0, 0, 0)
    y = h - 150
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Property Details:")
    y -= 25

    c.setFont("Helvetica", 11)
    details = [
        f"Type: {prop_data.get('property_type', 'N/A')}",
        f"Governorate: {prop_data.get('governorate', 'N/A')}",
        f"District: {prop_data.get('district', 'N/A')}",
        f"Size: {prop_data.get('size', 0):.0f} sqm",
        f"Bedrooms: {prop_data.get('bedrooms', 0):.0f}",
        f"Bathrooms: {prop_data.get('bathrooms', 0):.0f}",
    ]
    for d in details:
        c.drawString(60, y, d)
        y -= 20

    # Price
    y -= 20
    c.setFillColorRGB(0.9, 0.3, 0.4)
    c.rect(40, y - 70, w - 80, 70, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(60, y - 30, f"Estimated Price: {prop_data.get('price', 0):,.0f} EGP")
    c.setFont("Helvetica", 11)
    c.drawString(60, y - 55, f"Price per sqm: {prop_data.get('ppm2', 0):,.0f} EGP")

    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 9)
    c.drawString(40, 40, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


# ================================================================
# SIDEBAR - Language + Theme
# ================================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 AR" if st.session_state.lang == "en" else "🌐 EN", use_container_width=True):
            st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
            st.rerun()

    with col2:
        theme_icon = "☀️" if is_dark else "🌙"
        if st.button(theme_icon, use_container_width=True):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()

    st.markdown("---")


# ================================================================
# HEADER
# ================================================================
st.markdown(f"""
<div class="hero">
    <h1>{L['title']}</h1>
    <p>{L['subtitle']}</p>
    <div class="stats">{L['stats']}</div>
</div>
""", unsafe_allow_html=True)

if not loaded:
    st.stop()


# ================================================================
# TABS
# ================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    L['tab_predict'],
    L['tab_market'],
    L['tab_map'],
    L['tab_mortgage'],
    L['tab_compare'],
    L['tab_favorites'],
    L['tab_about'],
])


# ================================================================
# TAB 1: PREDICTION
# ================================================================
with tab1:
    col1, col2 = st.columns([1, 1.4])

    # ──────────────── LEFT: FORM ────────────────
    with col1:
        st.markdown(f'<div class="section-header">{L["prop_specs"]}</div>', unsafe_allow_html=True)

        governorate = st.selectbox(
            L["governorate"],
            ["Cairo", "Giza", "Matrouh", "Red Sea", "Alexandria", "Suez"],
        )

        districts_available = sorted(
            df[df["governorate"] == governorate]["district"].unique().tolist()
        )
        district = st.selectbox(L["district"], districts_available)

        property_type = st.selectbox(
            L["prop_type"],
            ["Apartment", "Villa", "Townhouse", "Duplex", "Penthouse",
             "Twin House", "iVilla", "Hotel Apartment", "Chalet"],
        )

        c1, c2 = st.columns(2)
        with c1:
            size = st.number_input(L["size"], 20, 5000, 200, 10)
            bathrooms = st.number_input(L["bathrooms"], 1, 15, 2)
        with c2:
            bedrooms = st.number_input(L["bedrooms"], 0, 15, 3)
            amenity_count = st.number_input(L["amenities"], 0, 20, 5)

        c3, c4 = st.columns(2)
        with c3:
            completion = st.selectbox(
                L["completion"],
                ["completed", "off_plan", "completed_primary", "off_plan_primary"],
            )
        with c4:
            furnished = st.selectbox(
                L["furnished"],
                ["Unfurnished", "Furnished", "PARTLY"],
            )

        images_count = st.slider(L["images"], 0, 30, 10)

        predict_btn = st.button(
            L["predict_btn"],
            type="primary",
            use_container_width=True,
        )

    # ──────────────── RIGHT: RESULT ────────────────
    with col2:
        if predict_btn:
            sample = df[(df["governorate"] == governorate) & (df["district"] == district)]
            lat = sample["latitude"].median() if len(sample) > 0 else 30.0444
            lon = sample["longitude"].median() if len(sample) > 0 else 31.2357

            # Build input
            input_data = {}
            for f in features:
                if f in cat_features:
                    input_data[f] = "Unknown"
                else:
                    input_data[f] = 0

            input_data.update({
                "size": size, "bedrooms": bedrooms, "bathrooms": bathrooms,
                "amenity_count": amenity_count, "images_count": images_count,
                "latitude": lat, "longitude": lon,
                "property_type": property_type, "governorate": governorate,
                "district": district, "compound": "No Compound",
                "completion_status": completion, "furnished": furnished,
                "seller_type": "Broker", "developer_name": "Unknown",
                "view": "Unknown", "finishing_type": "Unknown",
                "payment_method": "Unknown", "town": governorate,
                "area_per_room": size / max(bedrooms, 1),
                "total_rooms": bedrooms + bathrooms,
                "bed_bath_ratio": bedrooms / max(bathrooms, 1),
                "amenity_per_room": amenity_count / max(bedrooms + bathrooms, 1),
                "images_per_room": images_count / max(bedrooms + bathrooms, 1),
                "lat_x_lon": lat * lon,
                "distance_to_cairo": 0, "distance_to_coast": 0,
                "distance_cairo_sq": 0, "is_coastal": 0, "is_cairo_center": 0,
                "is_high_end": 1 if property_type in ["Villa", "Palace"] else 0,
                "is_luxury": 1 if property_type in ["Villa", "Penthouse", "Twin House"] else 0,
                "is_compound": 0, "is_premium": 0, "is_featured": 0,
                "walk_score": 50, "transit_score": 50,
                "amenity_score": amenity_count / 20,
                "floor_level": 3, "year_built": 2024, "has_premium_info": 0,
            })

            X_input = pd.DataFrame([input_data])[features]
            log_price = model.predict(X_input)[0]
            price = np.expm1(log_price)
            ppm2 = price / size

            # Save for PDF / favorites
            st.session_state.current_prediction = {
                "id": f"pred_{datetime.now().timestamp()}",
                "governorate": governorate,
                "district": district,
                "property_type": property_type,
                "size": size, "bedrooms": bedrooms, "bathrooms": bathrooms,
                "price": price, "ppm2": ppm2,
            }

            # ── RESULT CARD ──
            st.markdown(f"""
            <div class="result-card">
                <div class="label">{L["estimated_price"]}</div>
                <div class="price">{price:,.0f}</div>
                <div class="currency">EGP</div>
                <div class="ppm2">{L["price_per_m2"]}: {ppm2:,.0f} EGP/m²</div>
            </div>
            """, unsafe_allow_html=True)

            # ── MARKET COMPARISON ──
            market_median = df[
                (df["governorate"] == governorate) &
                (df["property_type"] == property_type)
            ]["price"].median()

            if pd.notna(market_median):
                diff_pct = (price - market_median) / market_median * 100
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric(L["market_avg"], f"{market_median:,.0f}")
                cc2.metric(L["difference"], f"{diff_pct:+.1f}%")
                cc3.metric("📍 Location", f"{district[:15]}")

            # ── ACTION BUTTONS ──
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2, b3, b4 = st.columns(4)

            with b1:
                if st.button(L["save"], use_container_width=True):
                    if st.session_state.current_prediction not in st.session_state.favorites:
                        st.session_state.favorites.append(st.session_state.current_prediction)
                        st.success("✅ Saved!")

            with b2:
                wa_text = f"Hi, I am interested in {property_type} in {district}, {size}m²"
                wa_url = f"https://wa.me/201001234567?text={wa_text}"
                st.markdown(
                    f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
                    f'<button style="width:100%;padding:0.6rem;background:#25D366;'
                    f'color:white;border:none;border-radius:10px;font-weight:700;'
                    f'cursor:pointer;">{L["whatsapp"]}</button></a>',
                    unsafe_allow_html=True,
                )

            with b3:
                st.markdown(
                    '<a href="tel:+201001234567" style="text-decoration:none;">'
                    '<button style="width:100%;padding:0.6rem;background:#667eea;'
                    'color:white;border:none;border-radius:10px;font-weight:700;'
                    'cursor:pointer;">📞 Call</button></a>',
                    unsafe_allow_html=True,
                )

            with b4:
                if PDF_AVAILABLE:
                    pdf_data = generate_property_pdf(st.session_state.current_prediction)
                    if pdf_data:
                        st.download_button(
                            L["pdf"],
                            data=pdf_data,
                            file_name=f"property_{district}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )

            # ── PROPERTY IMAGES ──
            st.markdown(f'<div class="section-header">{L["images_section"]}</div>', unsafe_allow_html=True)

            if CUSTOM_MODULES:
                images = get_property_images(
                    st.session_state.current_prediction["id"],
                    property_type,
                    count=5,
                )
                img_cols = st.columns(5)
                for i, url in enumerate(images):
                    with img_cols[i]:
                        st.image(url, use_container_width=True)

            # ── MAP + SIMILAR ──
            m_col, s_col = st.columns([1.2, 1])

            with m_col:
                st.markdown(f'<div class="section-header">{L["location"]}</div>', unsafe_allow_html=True)

                m = folium.Map(location=[lat, lon], zoom_start=13, tiles="CartoDB positron")
                folium.Marker(
                    [lat, lon],
                    popup=f"<b>{property_type}</b><br>{price:,.0f} EGP",
                    icon=folium.Icon(color="red", icon="home"),
                ).add_to(m)

                folium_static(m, width=600, height=300)

            with s_col:
                st.markdown(f'<div class="section-header">{L["similar"]}</div>', unsafe_allow_html=True)

                similar = df[
                    (df["governorate"] == governorate) &
                    (df["property_type"] == property_type) &
                    (df["size"].between(size * 0.8, size * 1.2))
                ].head(4)

                for _, row in similar.iterrows():
                    st.markdown(f"""
                    <div class="prop-card">
                        <div class="prop-card-body">
                            <p class="prop-price">{row["price"]:,.0f} EGP</p>
                            <p class="prop-title">{row["property_type"]} - {row["district"][:25]}</p>
                            <p class="prop-meta">📐 {row["size"]:.0f}m² | 🛏️ {row["bedrooms"]:.0f}BR | 🚿 {row["bathrooms"]:.0f}BA</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="empty">
                <div class="empty-icon">🏠</div>
                <div class="empty-title">{L["empty_prompt"]}</div>
                <div>{L["empty_desc"]}</div>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# TAB 2: MARKET ANALYSIS
# ================================================================
with tab2:
    st.markdown(f'<div class="section-header">{L["tab_market"]}</div>', unsafe_allow_html=True)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="card">
            <p class="card-title">📊 Listings</p>
            <p class="card-value">{len(df):,}</p>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="card">
            <p class="card-title">💰 Median Price</p>
            <p class="card-value">{df['price'].median()/1e6:.1f}M</p>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="card">
            <p class="card-title">📐 Median Size</p>
            <p class="card-value">{df['size'].median():.0f}m²</p>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="card">
            <p class="card-title">🏙️ Districts</p>
            <p class="card-value">{df['district'].nunique()}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(
            df, names="property_type", hole=0.5,
            title="🏢 Property Type Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        avg = df.groupby("governorate")["price"].median().sort_values()
        fig = px.bar(
            x=avg.values, y=avg.index, orientation="h",
            title="💰 Median Price by Governorate",
            labels={"x": "Price (EGP)", "y": ""},
            color=avg.values, color_continuous_scale="Viridis",
        )
        fig.update_layout(height=420, showlegend=False,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(
            df.sample(min(5000, len(df))), x="price", nbins=50,
            title="📊 Price Distribution",
            color_discrete_sequence=["#667eea"],
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        sample = df.sample(min(2000, len(df)))
        fig = px.scatter(
            sample, x="size", y="price", color="property_type",
            title="📐 Size vs Price", opacity=0.6,
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Detailed Table
    st.markdown('<div class="section-header">📋 Detailed Statistics</div>', unsafe_allow_html=True)
    table = df.groupby("governorate").agg({
        "price": ["count", "median", "mean", "min", "max"],
        "size": "median",
        "district": "nunique",
        "compound": "nunique",
    }).round(0)
    table.columns = ["Listings", "Median", "Mean", "Min", "Max", "Size", "Districts", "Compounds"]
    st.dataframe(table, use_container_width=True)


# ================================================================
# TAB 3: MAP
# ================================================================
with tab3:
    st.markdown(f'<div class="section-header">{L["tab_map"]}</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        map_gov = st.selectbox("Governorate", df["governorate"].unique(), key="map_g")
    with m2:
        map_type = st.selectbox("Type", ["All"] + list(df["property_type"].unique()), key="map_t")
    with m3:
        max_points = st.slider("Points", 100, 2000, 500, key="map_p")
    with m4:
        map_view = st.selectbox("View", ["Normal", "🔥 Heatmap"], key="map_v")

    filtered = df[df["governorate"] == map_gov]
    if map_type != "All":
        filtered = filtered[filtered["property_type"] == map_type]

    sample = filtered.sample(min(max_points, len(filtered))) if len(filtered) > 0 else filtered

    if len(sample) > 0:
        center_lat = sample["latitude"].median()
        center_lon = sample["longitude"].median()

        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="CartoDB positron")

        if map_view == "🔥 Heatmap":
            try:
                from folium.plugins import HeatMap
                heat_data = [[r["latitude"], r["longitude"],
                              min(r["price"] / 1e7, 1)] for _, r in sample.iterrows()]
                HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(m)
            except ImportError:
                st.warning("Heatmap plugin not available")

        else:
            median_price = sample["price"].median()
            for _, row in sample.iterrows():
                color = "red" if row["price"] > median_price else "blue"
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=5,
                    popup=f"<b>{row['property_type']}</b><br>💰 {row['price']:,.0f} EGP<br>📐 {row['size']:.0f} m²<br>📍 {row['district']}",
                    color=color, fill=True, fillOpacity=0.6,
                ).add_to(m)

        folium_static(m, width=1300, height=600)

        st.markdown(f"""
        <div class="card" style="margin-top:1rem;">
            <b>📊 Statistics:</b> {len(sample)} properties | 
            🔴 Above median | 🔵 Below median
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# TAB 4: MORTGAGE CALCULATOR
# ================================================================
with tab4:
    st.markdown(f'<div class="section-header">{L["tab_mortgage"]}</div>', unsafe_allow_html=True)

    mc1, mc2 = st.columns([1, 1])

    with mc1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        property_price = st.number_input(
            "💰 Property Price (EGP)",
            min_value=500_000, max_value=100_000_000,
            value=5_000_000, step=100_000,
        )
        down_pct = st.slider("📊 Down Payment (%)", 5, 50, 20)
        years = st.slider("📅 Years", 5, 30, 20)
        rate = st.slider("📈 Interest Rate (%)", 5.0, 25.0, 15.0, 0.5)
        st.markdown('</div>', unsafe_allow_html=True)

    with mc2:
        down_payment = property_price * down_pct / 100
        loan_amount = property_price - down_payment
        monthly_rate = (rate / 100) / 12
        n_months = years * 12

        if monthly_rate > 0:
            monthly = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_months) / ((1 + monthly_rate) ** n_months - 1)
        else:
            monthly = loan_amount / n_months

        total_paid = monthly * n_months
        total_interest = total_paid - loan_amount

        st.markdown(f"""
        <div class="result-card">
            <div class="label">💵 Monthly Payment</div>
            <div class="price">{monthly:,.0f}</div>
            <div class="currency">EGP / month</div>
        </div>
        """, unsafe_allow_html=True)

        kk1, kk2 = st.columns(2)
        kk1.metric("💰 Down Payment", f"{down_payment:,.0f}")
        kk1.metric("📊 Total Interest", f"{total_interest:,.0f}")
        kk2.metric("🏦 Loan Amount", f"{loan_amount:,.0f}")
        kk2.metric("💸 Total Paid", f"{total_paid:,.0f}")

    # Payment Schedule
    st.markdown('<div class="section-header">📅 Payment Schedule (First 12 months)</div>', unsafe_allow_html=True)

    schedule = []
    balance = loan_amount
    for month in range(1, min(13, n_months + 1)):
        interest = balance * monthly_rate
        principal = monthly - interest
        balance -= principal
        schedule.append({
            "Month": month,
            "Payment": f"{monthly:,.0f}",
            "Interest": f"{interest:,.0f}",
            "Principal": f"{principal:,.0f}",
            "Balance": f"{max(0, balance):,.0f}",
        })

    st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)

    # Pie Chart
    fig = go.Figure(data=[go.Pie(
        labels=["Down Payment", "Loan Amount", "Total Interest"],
        values=[down_payment, loan_amount, total_interest],
        hole=0.4,
        marker=dict(colors=["#667eea", "#764ba2", "#f5576c"]),
    )])
    fig.update_layout(
        title="📊 Cost Breakdown",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ================================================================
# TAB 5: COMPARE PROPERTIES
# ================================================================
with tab5:
    st.markdown(f'<div class="section-header">{L["tab_compare"]}</div>', unsafe_allow_html=True)

    st.markdown("### Select up to 4 properties to compare")

    # Filter
    fc1, fc2 = st.columns(2)
    with fc1:
        comp_gov = st.selectbox("Governorate", ["All"] + list(df["governorate"].unique()), key="comp_g")
    with fc2:
        comp_type = st.selectbox("Type", ["All"] + list(df["property_type"].unique()), key="comp_t")

    comp_df = df.copy()
    if comp_gov != "All":
        comp_df = comp_df[comp_df["governorate"] == comp_gov]
    if comp_type != "All":
        comp_df = comp_df[comp_df["property_type"] == comp_type]

    # Sample 20 for selection
    comp_sample = comp_df.sample(min(20, len(comp_df))) if len(comp_df) > 0 else comp_df

    if len(comp_sample) > 0:
        # Build options
        options = [
            f"{i+1}. {row['property_type']} - {row['district'][:20]} - {row['price']:,.0f} EGP - {row['size']:.0f}m²"
            for i, (_, row) in enumerate(comp_sample.iterrows())
        ]

        selected = st.multiselect(
            "Choose properties (max 4)",
            options,
            max_selections=4,
        )

        if len(selected) >= 2:
            # Extract selected
            selected_rows = []
            for sel in selected:
                idx = int(sel.split(".")[0]) - 1
                selected_rows.append(comp_sample.iloc[idx])

            # Comparison Table
            comp_data = {
                "Property Type": [r["property_type"] for r in selected_rows],
                "Governorate": [r["governorate"] for r in selected_rows],
                "District": [r["district"] for r in selected_rows],
                "Price (EGP)": [f"{r['price']:,.0f}" for r in selected_rows],
                "Size (m²)": [f"{r['size']:.0f}" for r in selected_rows],
                "Bedrooms": [f"{r['bedrooms']:.0f}" for r in selected_rows],
                "Bathrooms": [f"{r['bathrooms']:.0f}" for r in selected_rows],
                "Price/m²": [f"{r['price']/r['size']:,.0f}" for r in selected_rows],
                "Compound": [str(r["compound"])[:20] for r in selected_rows],
                "Completion": [r["completion_status"] for r in selected_rows],
                "Furnished": [r["furnished"] for r in selected_rows],
            }

            comp_table = pd.DataFrame(comp_data)
            st.dataframe(comp_table, use_container_width=True, hide_index=True)

            # Bar Chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"Prop {i+1}" for i in range(len(selected_rows))],
                y=[r["price"] for r in selected_rows],
                marker_color=["#667eea", "#764ba2", "#f5576c", "#00b894"][:len(selected_rows)],
                text=[f"{r['price']:,.0f}" for r in selected_rows],
                textposition="auto",
            ))
            fig.update_layout(
                title="💰 Price Comparison",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Price/m² chart
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=[f"Prop {i+1}" for i in range(len(selected_rows))],
                y=[r["price"]/r["size"] for r in selected_rows],
                marker_color="#667eea",
                text=[f"{r['price']/r['size']:,.0f}" for r in selected_rows],
                textposition="auto",
            ))
            fig2.update_layout(
                title="💵 Price per m² Comparison",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig2, use_container_width=True)

        elif len(selected) == 1:
            st.info("Select at least 2 properties to compare")
        else:
            st.info("Choose properties from the list above")


# ================================================================
# TAB 6: FAVORITES
# ================================================================
with tab6:
    st.markdown(f'<div class="section-header">{L["tab_favorites"]}</div>', unsafe_allow_html=True)

    favorites = st.session_state.favorites

    if len(favorites) == 0:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">💔</div>
            <div class="empty-title">No saved properties yet</div>
            <div>Go to Predict tab and save properties</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### You have **{len(favorites)}** saved properties")

        cols = st.columns(3)
        for i, fav in enumerate(favorites):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="prop-card">
                    <div class="prop-card-body">
                        <p class="prop-price">{fav['price']:,.0f} EGP</p>
                        <p class="prop-title">{fav['property_type']} - {fav['district'][:25]}</p>
                        <p class="prop-meta">
                            🏙️ {fav['governorate']}<br>
                            📐 {fav['size']:.0f}m² | 🛏️ {fav['bedrooms']:.0f}BR | 🚿 {fav['bathrooms']:.0f}BA<br>
                            💵 {fav['ppm2']:,.0f} EGP/m²
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🗑️ Remove", key=f"del_{i}", use_container_width=True):
                    st.session_state.favorites.pop(i)
                    st.rerun()

        # Clear all button
        st.markdown("---")
        if st.button("🗑️ Clear All Favorites", use_container_width=True):
            st.session_state.favorites = []
            st.rerun()


# ================================================================
# TAB 7: ABOUT
# ================================================================
with tab7:
    st.markdown(f'<div class="section-header">{L["tab_about"]}</div>', unsafe_allow_html=True)

    ac1, ac2 = st.columns(2)

    with ac1:
        st.markdown(f"""
        ### 📊 Dataset
        
        | Metric | Value |
        |--------|-------|
        | **Listings** | {len(df):,} |
        | **Governorates** | {df['governorate'].nunique()} |
        | **Property Types** | {df['property_type'].nunique()} |
        | **Districts** | {df['district'].nunique()} |
        | **Compounds** | {df['compound'].nunique()} |
        | **Sources** | Multiple |
        
        ### 🎯 Model
        
        | Metric | Value |
        |--------|-------|
        | **Algorithm** | CatBoost |
        | **R² Score** | **0.7061** |
        | **MAPE** | 40.52% |
        | **Features** | {len(features)} |
        | **Training Set** | 95,932 |
        | **Test Set** | 23,984 |
        """)

    with ac2:
        st.markdown("""
        ### 🛠️ Tech Stack
        
        - **Frontend**: Streamlit, Plotly, Folium
        - **ML**: CatBoost, XGBoost, LightGBM
        - **Data**: Pandas, NumPy
        - **PDF**: ReportLab
        - **Deployment**: Streamlit Cloud
        
        ### 📍 Supported Governorates
        
        1. 🏙️ Cairo (65,674 listings)
        2. 🏙️ Giza (30,374 listings)
        3. 🏖️ Matrouh (10,545 listings)
        4. 🌊 Red Sea (6,253 listings)
        5. 🌊 Alexandria (4,122 listings)
        6. 🚢 Suez (2,948 listings)
        
        ### 🎯 Features
        
        - 🎯 Price Prediction
        - 📊 Market Analysis
        - 🗺️ Interactive Map
        - 🧮 Mortgage Calculator
        - ⚖️ Compare Properties
        - ❤️ Favorites
        - 📄 PDF Reports
        - 📱 WhatsApp Contact
        - 🌐 Arabic/English
        - 🌙 Dark/Light Mode
        """)

    # Governorate stats
    st.markdown('<div class="section-header">📊 Governorate Statistics</div>', unsafe_allow_html=True)

    gov_stats = df.groupby("governorate").agg({
        "price": ["count", "median"],
        "district": "nunique",
        "compound": "nunique",
    }).round(0)
    gov_stats.columns = ["Listings", "Median Price", "Districts", "Compounds"]
    st.dataframe(gov_stats, use_container_width=True)


# ================================================================
# FOOTER
# ================================================================
st.markdown(f"""
<div class="footer">
    <p>🏠 <b>Egypt Real Estate AI</b> | Built with ❤️ using CatBoost + Streamlit</p>
    <p style="font-size:0.85rem;">119,916 listings | 6 governorates | R² = 0.7061</p>
    <p style="font-size:0.75rem; opacity:0.7;">© 2026 qamarsobhy7-source | MIT License</p>
</div>
""", unsafe_allow_html=True)
