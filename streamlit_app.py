"""
Egypt Real Estate AI - Beautiful App v12
Using original theme.py + dark_theme.py
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

# Setup path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Custom modules
from theme import (
    get_global_css, get_hero_html,
    get_section_header_html, get_step_header_html,
)
from dark_theme import get_css as get_theme_css

# PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Custom helpers
try:
    from mock_images import get_property_images
    IMAGES_OK = True
except ImportError:
    IMAGES_OK = False


# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Egypt Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "dark" not in st.session_state:
    st.session_state.dark = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "current_prediction" not in st.session_state:
    st.session_state.current_prediction = None

lang = st.session_state.lang
dark = st.session_state.dark


# ═══════════════════════════════════════════════════════════════
# LOAD MODEL & DATA
# ═══════════════════════════════════════════════════════════════
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

try:
    model, features, cat_features = load_model()
    df = load_data()
    LOADED = True
except Exception as e:
    LOADED = False
    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════
# APPLY THEME
# ═══════════════════════════════════════════════════════════════
st.markdown(get_theme_css(dark=dark, lang=lang), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════════════
T = {
    "ar": {
        "title": "🏠 الذكاء العقاري المصري",
        "badge": "🚀 مدعوم بالذكاء الاصطناعي",
        "subtitle": "توقع أسعار العقارات في مصر بدقة عالية",
        "stats_listings": "إعلان",
        "stats_govs": "محافظة",
        "stats_types": "نوع",
        "stats_districts": "منطقة",
        "tab_predict": "🎯 التوقع",
        "tab_market": "📊 السوق",
        "tab_map": "🗺️ الخريطة",
        "tab_mortgage": "🧮 الرهن",
        "tab_fav": "❤️ المفضلة",
        "form_title": "مواصفات العقار",
        "gov": "المحافظة",
        "district": "المنطقة",
        "ptype": "نوع العقار",
        "size": "المساحة (م²)",
        "beds": "غرف",
        "baths": "حمامات",
        "amenities": "كماليات",
        "completion": "حالة الإنشاء",
        "furnished": "الفرش",
        "images": "الصور",
        "predict_btn": "🔮 توقع السعر",
        "price": "السعر المتوقع",
        "ppm2": "سعر المتر",
        "market_avg": "متوسط السوق",
        "diff": "الفرق عن السوق",
        "save_btn": "❤️ حفظ",
        "wa_btn": "📱 واتساب",
        "call_btn": "📞 اتصال",
        "pdf_btn": "📄 تقرير",
        "images_title": "صور العقار",
        "similar": "عقارات مشابهة",
        "empty": "احسب سعر عقارك الآن",
    },
    "en": {
        "title": "🏠 Egypt Real Estate AI",
        "badge": "🚀 AI-Powered",
        "subtitle": "Predict property prices in Egypt with high accuracy",
        "stats_listings": "listings",
        "stats_govs": "governorates",
        "stats_types": "types",
        "stats_districts": "districts",
        "tab_predict": "🎯 Predict",
        "tab_market": "📊 Market",
        "tab_map": "🗺️ Map",
        "tab_mortgage": "🧮 Mortgage",
        "tab_fav": "❤️ Favorites",
        "form_title": "Property Specs",
        "gov": "Governorate",
        "district": "District",
        "ptype": "Property Type",
        "size": "Size (m²)",
        "beds": "Bedrooms",
        "baths": "Bathrooms",
        "amenities": "Amenities",
        "completion": "Completion",
        "furnished": "Furnished",
        "images": "Images",
        "predict_btn": "🔮 Predict Price",
        "price": "Estimated Price",
        "ppm2": "Price/m²",
        "market_avg": "Market Average",
        "diff": "vs Market",
        "save_btn": "❤️ Save",
        "wa_btn": "📱 WhatsApp",
        "call_btn": "📞 Call",
        "pdf_btn": "📄 Report",
        "images_title": "Property Images",
        "similar": "Similar Properties",
        "empty": "Calculate your property price",
    },
}

L = T[lang]


# ═══════════════════════════════════════════════════════════════
# PDF REPORT
# ═══════════════════════════════════════════════════════════════
def generate_pdf(prop):
    if not PDF_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    c.setFillColorRGB(0.4, 0.5, 0.9)
    c.rect(0, h - 100, w, 100, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, h - 60, "Egypt Real Estate AI")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 85, "Property Valuation Report")

    c.setFillColorRGB(0, 0, 0)
    y = h - 150
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Details:")
    y -= 25
    c.setFont("Helvetica", 11)

    for k, v in [
        ("Type", prop.get("property_type")),
        ("Governorate", prop.get("governorate")),
        ("District", prop.get("district")),
        ("Size", f"{prop.get('size', 0):.0f} m2"),
        ("Bedrooms", f"{prop.get('bedrooms', 0):.0f}"),
        ("Bathrooms", f"{prop.get('bathrooms', 0):.0f}"),
    ]:
        c.drawString(60, y, f"{k}: {v}")
        y -= 20

    y -= 20
    c.setFillColorRGB(0.9, 0.3, 0.4)
    c.rect(40, y - 70, w - 80, 70, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(60, y - 30, f"Price: {prop.get('price', 0):,.0f} EGP")
    c.setFont("Helvetica", 11)
    c.drawString(60, y - 55, f"Per m2: {prop.get('ppm2', 0):,.0f} EGP")

    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 9)
    c.drawString(40, 40, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buf.seek(0)
    return buf.getvalue()


if not LOADED:
    st.stop()



# ═══════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-section">
    <div class="hero-badge">{L['badge']}</div>
    <h1 class="hero-title">{L['title']}</h1>
    <p class="hero-subtitle">{L['subtitle']}</p>
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{len(df):,}</div>
            <div class="stat-label">{L['stats_listings']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{df['governorate'].nunique()}</div>
            <div class="stat-label">{L['stats_govs']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{df['property_type'].nunique()}</div>
            <div class="stat-label">{L['stats_types']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{df['district'].nunique()}</div>
            <div class="stat-label">{L['stats_districts']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TOP CONTROLS (lang + dark)
# ═══════════════════════════════════════════════════════════════
top1, top2, top3 = st.columns([1, 1, 6])

with top1:
    if st.button("🌐 " + ("EN" if lang == "ar" else "AR"), use_container_width=True, key="lang_btn"):
        st.session_state.lang = "en" if lang == "ar" else "ar"
        st.rerun()

with top2:
    theme_icon = "☀️" if dark else "🌙"
    if st.button(theme_icon + " Theme", use_container_width=True, key="theme_btn"):
        st.session_state.dark = not dark
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    L["tab_predict"],
    L["tab_market"],
    L["tab_map"],
    L["tab_mortgage"],
    L["tab_fav"],
])


# ═══════════════════════════════════════════════════════════════
# TAB 1: PREDICTION
# ═══════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1.4], gap="large")

    # ──────────────── LEFT: FORM ────────────────
    with col1:
        st.markdown(f'<div class="form-card">', unsafe_allow_html=True)
        st.markdown(get_section_header_html("📝", L["form_title"]), unsafe_allow_html=True)

        governorate = st.selectbox(
            f"🏙️ {L['gov']}",
            ["Cairo", "Giza", "Matrouh", "Red Sea", "Alexandria", "Suez"],
        )

        districts_available = sorted(
            df[df["governorate"] == governorate]["district"].unique().tolist()
        )
        district = st.selectbox(f"📍 {L['district']}", districts_available)

        property_type = st.selectbox(
            f"🏢 {L['ptype']}",
            ["Apartment", "Villa", "Townhouse", "Duplex", "Penthouse",
             "Twin House", "iVilla", "Hotel Apartment", "Chalet"],
        )

        c1, c2 = st.columns(2)
        with c1:
            size = st.number_input(f"📐 {L['size']}", 20, 5000, 200, 10)
            bathrooms = st.number_input(f"🚿 {L['baths']}", 1, 15, 2)
        with c2:
            bedrooms = st.number_input(f"🛏️ {L['beds']}", 0, 15, 3)
            amenity_count = st.number_input(f"✨ {L['amenities']}", 0, 20, 5)

        c3, c4 = st.columns(2)
        with c3:
            completion = st.selectbox(
                f"🏗️ {L['completion']}",
                ["completed", "off_plan", "completed_primary", "off_plan_primary"],
            )
        with c4:
            furnished = st.selectbox(
                f"🛋️ {L['furnished']}",
                ["Unfurnished", "Furnished", "PARTLY"],
            )

        images_count = st.slider(f"📸 {L['images']}", 0, 30, 10)

        st.markdown("</div>", unsafe_allow_html=True)

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

            st.session_state.current_prediction = {
                "id": f"pred_{datetime.now().timestamp()}",
                "governorate": governorate,
                "district": district,
                "property_type": property_type,
                "size": size, "bedrooms": bedrooms, "bathrooms": bathrooms,
                "price": price, "ppm2": ppm2,
            }

            # Result Card
            st.markdown(f"""
            <div class="property-preview">
                <div style="padding: 28px;">
                    <div style="font-size:14px; opacity:0.9; font-weight:700;
                                letter-spacing:1px; text-transform:uppercase;">
                        {L['price']}
                    </div>
                    <div style="font-size:52px; font-weight:900; margin:12px 0; line-height:1;">
                        {price:,.0f}
                    </div>
                    <div style="font-size:18px; opacity:0.95;">EGP</div>
                    <div style="background:rgba(255,255,255,0.2); padding:10px 20px;
                                border-radius:100px; display:inline-block;
                                margin-top:16px; font-weight:700;">
                        {L['ppm2']}: {ppm2:,.0f} EGP/m²
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Market comparison
            market_median = df[
                (df["governorate"] == governorate) &
                (df["property_type"] == property_type)
            ]["price"].median()

            if pd.notna(market_median):
                diff_pct = (price - market_median) / market_median * 100
                st.markdown("<br>", unsafe_allow_html=True)
                k1, k2, k3 = st.columns(3)
                k1.metric(L["market_avg"], f"{market_median:,.0f}")
                k2.metric(L["diff"], f"{diff_pct:+.1f}%")
                k3.metric("📍", f"{district[:15]}")

            # Actions
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2, b3, b4 = st.columns(4)

            with b1:
                if st.button(L["save_btn"], use_container_width=True, key="save_pred"):
                    if st.session_state.current_prediction not in st.session_state.favorites:
                        st.session_state.favorites.append(st.session_state.current_prediction)
                        st.success("✅")

            with b2:
                wa_text = f"Interested in {property_type} in {district}, {size}m²"
                wa_url = f"https://wa.me/201001234567?text={wa_text}"
                st.markdown(
                    f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
                    f'<button style="width:100%;padding:8px;background:#25D366;'
                    f'color:white;border:none;border-radius:12px;font-weight:800;'
                    f'font-size:14px;cursor:pointer;">{L["wa_btn"]}</button></a>',
                    unsafe_allow_html=True,
                )

            with b3:
                st.markdown(
                    '<a href="tel:+201001234567" style="text-decoration:none;">'
                    f'<button style="width:100%;padding:8px;background:#6366f1;'
                    'color:white;border:none;border-radius:12px;font-weight:800;'
                    f'font-size:14px;cursor:pointer;">{L["call_btn"]}</button></a>',
                    unsafe_allow_html=True,
                )

            with b4:
                if PDF_AVAILABLE:
                    pdf_data = generate_pdf(st.session_state.current_prediction)
                    if pdf_data:
                        st.download_button(
                            L["pdf_btn"],
                            data=pdf_data,
                            file_name=f"property_{district}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="pdf_dl",
                        )

            # Images
            if IMAGES_OK:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(get_section_header_html("📸", L["images_title"]), unsafe_allow_html=True)
                imgs = get_property_images(
                    st.session_state.current_prediction["id"], property_type, 5
                )
                img_cols = st.columns(5)
                for i, u in enumerate(imgs):
                    with img_cols[i]:
                        st.image(u, use_container_width=True)

            # Similar
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(get_section_header_html("🏘️", L["similar"]), unsafe_allow_html=True)
            similar = df[
                (df["governorate"] == governorate) &
                (df["property_type"] == property_type) &
                (df["size"].between(size * 0.8, size * 1.2))
            ].head(3)

            for _, row in similar.iterrows():
                st.markdown(f"""
                <div class="metric-card" style="text-align:left; margin-bottom:10px;">
                    <div class="metric-value" style="font-size:18px;">
                        {row['price']:,.0f} EGP
                    </div>
                    <div class="metric-label" style="font-size:13px; text-transform:none; letter-spacing:0;">
                        {row['property_type']} · {row['district'][:30]}
                    </div>
                    <div style="margin-top:6px; color:#6b7280; font-size:13px;">
                        📐 {row['size']:.0f}m² · 🛏️ {row['bedrooms']:.0f}BR · 🚿 {row['bathrooms']:.0f}BA
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div style="text-align:center; padding:5rem 2rem; opacity:0.7;">
                <div style="font-size:6rem; margin-bottom:1rem;">🏠</div>
                <div style="font-size:1.4rem; font-weight:800; margin-bottom:0.5rem;">
                    {L['empty']}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2: MARKET
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown(get_section_header_html("📊", L["tab_market"]), unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Listings</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['price'].median()/1e6:.1f}M</div>
            <div class="metric-label">Median Price</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['size'].median():.0f}m²</div>
            <div class="metric-label">Median Size</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['compound'].nunique()}</div>
            <div class="metric-label">Compounds</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(
            df, names="property_type", hole=0.5,
            title="🏢 Property Types",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        avg = df.groupby("governorate")["price"].median().sort_values()
        fig = px.bar(
            x=avg.values, y=avg.index, orientation="h",
            title="💰 Median Price by Governorate",
            color=avg.values, color_continuous_scale="Viridis",
        )
        fig.update_layout(height=420, showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(
            df.sample(min(5000, len(df))), x="price", nbins=50,
            title="📊 Price Distribution",
            color_discrete_sequence=["#6366f1"],
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        sample = df.sample(min(2000, len(df)))
        fig = px.scatter(
            sample, x="size", y="price", color="property_type",
            title="📐 Size vs Price", opacity=0.6,
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(get_section_header_html("📋", "Detailed Stats"), unsafe_allow_html=True)
    table = df.groupby("governorate").agg({
        "price": ["count", "median", "mean", "min", "max"],
        "size": "median",
        "district": "nunique",
        "compound": "nunique",
    }).round(0)
    table.columns = ["Listings", "Median", "Mean", "Min", "Max", "Size", "Districts", "Compounds"]
    st.dataframe(table, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# TAB 3: MAP
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(get_section_header_html("🗺️", L["tab_map"]), unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        map_gov = st.selectbox("Governorate", df["governorate"].unique(), key="map_g")
    with m2:
        map_type = st.selectbox("Type", ["All"] + list(df["property_type"].unique()), key="map_t")
    with m3:
        max_pts = st.slider("Points", 100, 2000, 500, key="map_p")
    with m4:
        map_view = st.selectbox("View", ["Normal", "🔥 Heatmap"], key="map_v")

    filtered = df[df["governorate"] == map_gov]
    if map_type != "All":
        filtered = filtered[filtered["property_type"] == map_type]

    sample = filtered.sample(min(max_pts, len(filtered))) if len(filtered) > 0 else filtered

    if len(sample) > 0:
        center_lat = sample["latitude"].median()
        center_lon = sample["longitude"].median()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="CartoDB positron")

        if map_view == "🔥 Heatmap":
            try:
                from folium.plugins import HeatMap
                hd = [[r["latitude"], r["longitude"], min(r["price"] / 1e7, 1)] 
                      for _, r in sample.iterrows()]
                HeatMap(hd, radius=15, blur=20).add_to(m)
            except:
                st.warning("Heatmap unavailable")

        else:
            median_price = sample["price"].median()
            for _, row in sample.iterrows():
                color = "red" if row["price"] > median_price else "blue"
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=5,
                    popup=f"<b>{row['property_type']}</b><br>💰 {row['price']:,.0f} EGP<br>📐 {row['size']:.0f} m²",
                    color=color, fill=True, fillOpacity=0.6,
                ).add_to(m)

        folium_static(m, width=1300, height=600)


# ═══════════════════════════════════════════════════════════════
# TAB 4: MORTGAGE
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown(get_section_header_html("🧮", L["tab_mortgage"]), unsafe_allow_html=True)

    mc1, mc2 = st.columns(2)

    with mc1:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        p_price = st.number_input("💰 Property Price (EGP)", 500_000, 100_000_000, 5_000_000, 100_000)
        down_pct = st.slider("📊 Down Payment (%)", 5, 50, 20)
        years = st.slider("📅 Years", 5, 30, 20)
        rate = st.slider("📈 Interest Rate (%)", 5.0, 25.0, 15.0, 0.5)
        st.markdown('</div>', unsafe_allow_html=True)

    with mc2:
        down_payment = p_price * down_pct / 100
        loan = p_price - down_payment
        mr = (rate / 100) / 12
        n = years * 12
        monthly = loan * (mr * (1 + mr) ** n) / ((1 + mr) ** n - 1) if mr > 0 else loan / n
        total = monthly * n
        interest = total - loan

        st.markdown(f"""
        <div class="property-preview" style="text-align:center;">
            <div style="padding:28px;">
                <div style="font-size:14px; font-weight:700; letter-spacing:1px;
                            text-transform:uppercase; opacity:0.9;">
                    Monthly Payment
                </div>
                <div style="font-size:48px; font-weight:900; margin:12px 0; line-height:1;">
                    {monthly:,.0f}
                </div>
                <div style="font-size:16px; opacity:0.9;">EGP/month</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        k1, k2 = st.columns(2)
        k1.metric("💰 Down Payment", f"{down_payment:,.0f}")
        k1.metric("📊 Interest", f"{interest:,.0f}")
        k2.metric("🏦 Loan", f"{loan:,.0f}")
        k2.metric("💸 Total", f"{total:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(get_section_header_html("📅", "Payment Schedule"), unsafe_allow_html=True)

    schedule = []
    bal = loan
    for month in range(1, min(13, n + 1)):
        i = bal * mr
        p = monthly - i
        bal -= p
        schedule.append({
            "Month": month,
            "Payment": f"{monthly:,.0f}",
            "Interest": f"{i:,.0f}",
            "Principal": f"{p:,.0f}",
            "Balance": f"{max(0, bal):,.0f}",
        })
    st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 5: FAVORITES
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown(get_section_header_html("❤️", L["tab_fav"]), unsafe_allow_html=True)

    favs = st.session_state.favorites

    if len(favs) == 0:
        st.markdown("""
        <div style="text-align:center; padding:5rem 2rem; opacity:0.7;">
            <div style="font-size:6rem; margin-bottom:1rem;">💔</div>
            <div style="font-size:1.4rem; font-weight:800;">
                No saved properties yet
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### You have **{len(favs)}** saved properties")
        cols = st.columns(3)
        for i, fav in enumerate(favs):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card" style="text-align:left; margin-bottom:10px;">
                    <div class="metric-value" style="font-size:20px;">
                        {fav['price']:,.0f} EGP
                    </div>
                    <div class="metric-label" style="font-size:13px; text-transform:none;">
                        {fav['property_type']} · {fav['district'][:25]}
                    </div>
                    <div style="margin-top:8px; color:#6b7280; font-size:12px;">
                        🏙️ {fav['governorate']}<br>
                        📐 {fav['size']:.0f}m² · 🛏️ {fav['bedrooms']:.0f}BR
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🗑️ Remove", key=f"del_{i}", use_container_width=True):
                    st.session_state.favorites.pop(i)
                    st.rerun()


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding:2rem 0; margin-top:3rem; 
            border-top:1px solid rgba(0,0,0,0.1); opacity:0.7;">
    <p style="font-weight:700;">🏠 Egypt Real Estate AI</p>
    <p style="font-size:0.85rem;">119,916 listings · 6 governorates · R² = 0.7061</p>
</div>
""", unsafe_allow_html=True)
