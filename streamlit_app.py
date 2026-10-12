"""
Egypt Real Estate AI - Clean Rebuild
Design: Nawy-inspired
Rules: No emojis | Full language separation
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from nawy_theme import get_css, get_theme
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
    calculate_roi, recommend_similar_properties,
)

st.set_page_config(
    page_title="Egypt Real Estate AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_defaults = {
    "lang": "en", "dark": False, "favorites": [],
    "selected_features": [], "current_prediction": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

lang = st.session_state.lang
dark = st.session_state.dark

TEXTS = {
    "en": {
        "brand_prefix": "Egypt", "brand_suffix": "Real Estate AI",
        "hero_title": "Real Estate Price Estimator",
        "hero_sub": "Instant valuations for the Egyptian real estate market",
        "stat_accuracy": "Accuracy", "stat_error": "Avg Error",
        "stat_gov": "Governorates", "stat_listings": "Listings",
        "nav_lang": "AR",
        "theme_dark": "Dark", "theme_light": "Light",
        "section_types": "Browse by Property Type",
        "section_areas": "Popular Areas",
        "section_compounds": "Latest Compounds",
        "show_more": "Show More",
        "tab_estimator": "Price Estimator",
        "tab_market": "Market Analysis",
        "tab_mortgage": "Mortgage Calculator",
        "tab_favorites": "Favorites",
        "location": "Location", "details": "Details", "features": "Features",
        "governorate": "Governorate", "city": "City",
        "district": "District", "compound": "Compound",
        "no_compound": "None",
        "property_type": "Property Type",
        "size": "Size (sqm)", "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms", "floor": "Floor",
        "living_rooms": "Living Rooms", "kitchens": "Kitchens",
        "finishing": "Finishing", "furnished": "Furnished",
        "additional_features": "Additional Features",
        "select_features": "Select available features",
        "calculate": "Calculate Price",
        "calculating": "Calculating...",
        "result_title": "Estimated Price",
        "per_sqm": "Price per sqm",
        "confidence": "Confidence",
        "price_range": "Range",
        "vs_market": "vs. Market",
        "save": "Save", "saved": "Saved",
        "whatsapp": "WhatsApp", "call": "Call", "pdf": "PDF Report",
        "above_market": "above market",
        "below_market": "below market",
        "at_market": "at market level",
        "empty_title": "No favorites yet",
        "empty_desc": "Save properties to see them here",
        "pt_apartment": "Apartments", "pt_villa": "Villas",
        "pt_duplex": "Duplexes", "pt_townhouse": "Townhouses",
        "pt_penthouse": "Penthouses", "pt_chalet": "Chalets",
        "fin_core": "Core & Shell", "fin_semi": "Semi Finished",
        "fin_finished": "Finished", "fin_super": "Super Lux",
        "fur_no": "Unfurnished", "fur_partly": "Partly Furnished",
        "fur_yes": "Furnished",
        "feat_garden": "Garden", "feat_pool": "Pool",
        "feat_garage": "Garage", "feat_security": "Security 24/7",
        "feat_gym": "Gym", "feat_elevator": "Elevator",
        "feat_balcony": "Balcony", "feat_view": "View",
        "feat_mall": "Mall", "feat_mosque": "Mosque",
        "feat_club": "Sports Club", "feat_sea": "Sea Front",
        "mortgage_loan": "Loan Amount (EGP)",
        "mortgage_rate": "Annual Interest Rate (%)",
        "mortgage_years": "Years",
        "mortgage_monthly": "Monthly Payment",
        "mortgage_total": "Total Payment",
        "mortgage_interest": "Total Interest",
        "footer_tagline": "AI-powered real estate valuation for Egypt",
        "footer_rights": "All rights reserved",
        "currency": "EGP",
    },
    "ar": {
        "brand_prefix": "الذكاء", "brand_suffix": "العقاري",
        "hero_title": "حاسبة أسعار العقارات",
        "hero_sub": "تقديرات فورية لسوق العقارات المصري",
        "stat_accuracy": "الدقة", "stat_error": "متوسط الخطأ",
        "stat_gov": "محافظة", "stat_listings": "إعلان",
        "nav_lang": "EN",
        "theme_dark": "داكن", "theme_light": "فاتح",
        "section_types": "تصفح حسب نوع العقار",
        "section_areas": "أشهر المناطق",
        "section_compounds": "أحدث الكمبوندات",
        "show_more": "أظهر المزيد",
        "tab_estimator": "حاسبة الأسعار",
        "tab_market": "تحليل السوق",
        "tab_mortgage": "حاسبة الرهن",
        "tab_favorites": "المفضلة",
        "location": "الموقع", "details": "التفاصيل", "features": "المميزات",
        "governorate": "المحافظة", "city": "المدينة",
        "district": "الحي", "compound": "كمبوند",
        "no_compound": "لا يوجد",
        "property_type": "نوع العقار",
        "size": "المساحة (م²)", "bedrooms": "غرف النوم",
        "bathrooms": "الحمامات", "floor": "الطابق",
        "living_rooms": "الصالونات", "kitchens": "المطابخ",
        "finishing": "التشطيب", "furnished": "الفرش",
        "additional_features": "مميزات إضافية",
        "select_features": "اختر المميزات المتاحة",
        "calculate": "احسب السعر",
        "calculating": "جاري الحساب...",
        "result_title": "السعر المتوقع",
        "per_sqm": "سعر المتر",
        "confidence": "نسبة الثقة",
        "price_range": "النطاق السعري",
        "vs_market": "مقارنة بالسوق",
        "save": "حفظ", "saved": "تم الحفظ",
        "whatsapp": "واتساب", "call": "اتصال", "pdf": "تقرير PDF",
        "above_market": "أعلى من السوق",
        "below_market": "أقل من السوق",
        "at_market": "في مستوى السوق",
        "empty_title": "لا توجد مفضلات بعد",
        "empty_desc": "احفظ العقارات لتظهر هنا",
        "pt_apartment": "شقق", "pt_villa": "فيلل",
        "pt_duplex": "دوبلكس", "pt_townhouse": "تاون هاوس",
        "pt_penthouse": "بنتهاوس", "pt_chalet": "شاليهات",
        "fin_core": "طوب أحمر", "fin_semi": "نصف تشطيب",
        "fin_finished": "تشطيب كامل", "fin_super": "سوبر لوكس",
        "fur_no": "غير مفروش", "fur_partly": "مفروش جزئياً",
        "fur_yes": "مفروش",
        "feat_garden": "حديقة", "feat_pool": "حمام سباحة",
        "feat_garage": "جراج", "feat_security": "أمن 24/7",
        "feat_gym": "جيم", "feat_elevator": "أسانسير",
        "feat_balcony": "بلكونة", "feat_view": "إطلالة",
        "feat_mall": "مول تجاري", "feat_mosque": "مسجد",
        "feat_club": "نادي رياضي", "feat_sea": "على البحر",
        "mortgage_loan": "مبلغ التمويل (جنيه)",
        "mortgage_rate": "سعر الفائدة السنوي (%)",
        "mortgage_years": "عدد السنوات",
        "mortgage_monthly": "القسط الشهري",
        "mortgage_total": "إجمالي المدفوع",
        "mortgage_interest": "إجمالي الفوائد",
        "footer_tagline": "تقدير أسعار العقارات بالذكاء الاصطناعي لمصر",
        "footer_rights": "جميع الحقوق محفوظة",
        "currency": "ج.م",
    },
}
T = TEXTS[lang]

st.markdown(get_css(dark=dark, lang=lang), unsafe_allow_html=True)

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
except Exception as e:
    st.error(f"Load error: {e}")
    st.stop()

def nm(obj):
    if obj is None: return ""
    if isinstance(obj, str): return obj
    if lang in obj and obj[lang]: return obj[lang]
    return obj.get("en", "")


# ═══ NAVBAR ═══
nav1, nav2, nav3 = st.columns([6, 1, 1])
with nav1:
    st.markdown(
        f'<div class="navbar-logo">{T["brand_prefix"]} <span>{T["brand_suffix"]}</span></div>',
        unsafe_allow_html=True,
    )
with nav2:
    if st.button(T["nav_lang"], key="lang_btn"):
        st.session_state.lang = "ar" if lang == "en" else "en"
        st.rerun()
with nav3:
    theme_label = T["theme_light"] if dark else T["theme_dark"]
    if st.button(theme_label, key="theme_btn"):
        st.session_state.dark = not dark
        st.rerun()

# ═══ HERO ═══
metrics = metadata["metrics"]
training = metadata["training_info"]
n_gov = sum(1 for g in hierarchy["governorates"] if g["listings"] > 0)

st.markdown(
    '<div class="hero">'
    '<div class="hero-title">' + T["hero_title"] + '</div>'
    '<div class="hero-subtitle">' + T["hero_sub"] + '</div>'
    '<div class="hero-stats">'
    '<div class="hero-stat"><div class="hero-stat-value">' + f'{metrics["r2"]:.4f}' + '</div><div class="hero-stat-label">' + T["stat_accuracy"] + '</div></div>'
    '<div class="hero-stat"><div class="hero-stat-value">' + f'{metrics["mape"]:.1f}%' + '</div><div class="hero-stat-label">' + T["stat_error"] + '</div></div>'
    '<div class="hero-stat"><div class="hero-stat-value">' + str(n_gov) + '</div><div class="hero-stat-label">' + T["stat_gov"] + '</div></div>'
    '<div class="hero-stat"><div class="hero-stat-value">' + f'{training["n_total"]:,}' + '</div><div class="hero-stat-label">' + T["stat_listings"] + '</div></div>'
    '</div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="content-area">', unsafe_allow_html=True)

# ═══ PROPERTY TYPES ═══
st.markdown(
    '<div class="section-head">'
    '<div class="section-title">' + T["section_types"] + '</div>'
    '<a class="section-link">' + T["show_more"] + '</a>'
    '</div>',
    unsafe_allow_html=True,
)

ptype_items = [
    ("AP", T["pt_apartment"], "45,200"),
    ("VI", T["pt_villa"], "8,500"),
    ("TH", T["pt_townhouse"], "2,100"),
    ("DX", T["pt_duplex"], "3,200"),
    ("PH", T["pt_penthouse"], "950"),
    ("CH", T["pt_chalet"], "12,800"),
]
pt_cols = st.columns(6)
for i, (code, name, count) in enumerate(ptype_items):
    with pt_cols[i]:
        st.markdown(
            '<div class="ptype-card">'
            '<div class="ptype-icon">' + code + '</div>'
            '<div class="ptype-name">' + name + '</div>'
            '<div class="ptype-count">' + count + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

# ═══ AREAS ═══
st.markdown(
    '<div class="section-head">'
    '<div class="section-title">' + T["section_areas"] + '</div>'
    '<a class="section-link">' + T["show_more"] + '</a>'
    '</div>',
    unsafe_allow_html=True,
)

if lang == "ar":
    areas = [
        ("القاهرة الجديدة", "365 كمبوند"),
        ("مدينة 6 أكتوبر", "163 كمبوند"),
        ("العاصمة الإدارية", "245 كمبوند"),
        ("مدينة المستقبل", "98 كمبوند"),
        ("الساحل الشمالي", "210 كمبوند"),
        ("العين السخنة", "78 كمبوند"),
    ]
else:
    areas = [
        ("New Cairo", "365 compounds"),
        ("6 October City", "163 compounds"),
        ("New Capital", "245 compounds"),
        ("Mostakbal City", "98 compounds"),
        ("North Coast", "210 compounds"),
        ("Ain Sokhna", "78 compounds"),
    ]

area_cols = st.columns(6)
for i, (name, count) in enumerate(areas):
    with area_cols[i]:
        st.markdown(
            '<div class="area-card">'
            '<div class="area-name">' + name + '</div>'
            '<div class="area-count">' + count + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

# ═══ COMPOUNDS ═══
st.markdown(
    '<div class="section-head">'
    '<div class="section-title">' + T["section_compounds"] + '</div>'
    '<a class="section-link">' + T["show_more"] + '</a>'
    '</div>',
    unsafe_allow_html=True,
)

if lang == "ar":
    compounds = [
        ("ماونتن فيو 1.1 - التجمع", "14 وحدة", "14,500,000"),
        ("ماونتن فيو رأس الحكمة", "32 وحدة", "8,200,000"),
        ("مكادي هايتس - مكادي", "70 وحدة", "6,900,000"),
    ]
    price_prefix = "يبدأ من"
else:
    compounds = [
        ("Mountain View 1.1 - Fifth Settlement", "14 units", "14,500,000"),
        ("Mountain View Ras El Hekma", "32 units", "8,200,000"),
        ("Makadi Heights - Makadi", "70 units", "6,900,000"),
    ]
    price_prefix = "From"

comp_cols = st.columns(3)
for i, (name, units, price) in enumerate(compounds):
    with comp_cols[i]:
        st.markdown(
            '<div class="comp-card">'
            '<div class="comp-title">' + name + '</div>'
            '<div class="comp-units">' + units + '</div>'
            '<div class="comp-price">' + price_prefix + ' ' + price + ' ' + T["currency"] + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

# ═══ TABS ═══
tab1, tab2, tab3, tab4 = st.tabs([
    T["tab_estimator"],
    T["tab_market"],
    T["tab_mortgage"],
    T["tab_favorites"],
])


# ═══ TAB 1: ESTIMATOR ═══
with tab1:
    col_form, col_result = st.columns([5, 7], gap="large")

    with col_form:
        st.markdown('<div class="form-section">' + T["location"] + '</div>', unsafe_allow_html=True)

        gov_options = [g for g in hierarchy["governorates"] if g["listings"] > 0]
        gov_labels = [nm(g) + " (" + f'{g["listings"]:,}' + ")" for g in gov_options]
        gov_idx = st.selectbox(T["governorate"], range(len(gov_options)),
                                format_func=lambda i: gov_labels[i], key="sel_gov")
        selected_gov = gov_options[gov_idx]

        cities = selected_gov.get("cities", [])
        if cities:
            city_labels = [nm(c) + " (" + f'{c["listings"]:,}' + ")" for c in cities]
            city_idx = st.selectbox(T["city"], range(len(cities)),
                                     format_func=lambda i: city_labels[i], key="sel_city")
            selected_city = cities[city_idx]
        else:
            selected_city = {"districts": [], "compounds": []}

        districts = selected_city.get("districts", [])
        if districts:
            dist_labels = [nm(d) + " (" + f'{d["listings"]:,}' + ")" for d in districts]
            dist_idx = st.selectbox(T["district"], range(len(districts)),
                                     format_func=lambda i: dist_labels[i], key="sel_dist")
            selected_district = districts[dist_idx]
        else:
            selected_district = {"en": "Unknown", "ar": "غير معروف"}

        compounds_list = selected_city.get("compounds", [])
        if compounds_list:
            comp_labels = ["-- " + T["no_compound"] + " --"] + [nm(c) for c in compounds_list]
            comp_idx = st.selectbox(T["compound"], range(len(comp_labels)),
                                     format_func=lambda i: comp_labels[i], key="sel_comp")
            selected_compound = compounds_list[comp_idx - 1] if comp_idx > 0 else {"en": "No Compound", "ar": "لا يوجد"}
        else:
            selected_compound = {"en": "No Compound", "ar": "لا يوجد"}

        st.markdown('<div class="form-section">' + T["details"] + '</div>', unsafe_allow_html=True)

        ptype_keys = ["Apartment", "Villa", "Townhouse", "Duplex", "Penthouse", "Chalet"]
        ptype_labels = {
            "Apartment": T["pt_apartment"], "Villa": T["pt_villa"],
            "Townhouse": T["pt_townhouse"], "Duplex": T["pt_duplex"],
            "Penthouse": T["pt_penthouse"], "Chalet": T["pt_chalet"],
        }
        selected_ptype = st.selectbox(
            T["property_type"], ptype_keys,
            format_func=lambda k: ptype_labels[k], key="sel_ptype"
        )

        c1, c2 = st.columns(2)
        with c1:
            size = st.number_input(T["size"], 30, 5000, 200, 10, key="inp_size")
            bathrooms = st.number_input(T["bathrooms"], 1, 15, 2, key="inp_baths")
            living_rooms = st.number_input(T["living_rooms"], 0, 5, 1, key="inp_living")
        with c2:
            bedrooms = st.number_input(T["bedrooms"], 0, 15, 3, key="inp_beds")
            kitchens = st.number_input(T["kitchens"], 0, 3, 1, key="inp_kitchen")
            floor = st.number_input(T["floor"], 0, 50, 3, key="inp_floor")

        st.markdown('<div class="form-section">' + T["features"] + '</div>', unsafe_allow_html=True)

        fin_keys = ["Core & Shell", "Semi Finished", "Finished", "Super Lux"]
        fin_labels = {"Core & Shell": T["fin_core"], "Semi Finished": T["fin_semi"],
                      "Finished": T["fin_finished"], "Super Lux": T["fin_super"]}
        finishing = st.selectbox(T["finishing"], fin_keys,
                                  format_func=lambda k: fin_labels[k], key="inp_finishing")

        fur_keys = ["Unfurnished", "PARTLY", "Furnished"]
        fur_labels = {"Unfurnished": T["fur_no"], "PARTLY": T["fur_partly"], "Furnished": T["fur_yes"]}
        furnished = st.selectbox(T["furnished"], fur_keys,
                                  format_func=lambda k: fur_labels[k], key="inp_furnished")

        st.markdown('<div class="form-section">' + T["additional_features"] + '</div>', unsafe_allow_html=True)
        st.caption(T["select_features"])

        feat_items = [
            ("garden", T["feat_garden"]), ("pool", T["feat_pool"]),
            ("garage", T["feat_garage"]), ("security", T["feat_security"]),
            ("gym", T["feat_gym"]), ("elevator", T["feat_elevator"]),
            ("balcony", T["feat_balcony"]), ("view", T["feat_view"]),
            ("mall", T["feat_mall"]), ("mosque", T["feat_mosque"]),
            ("club", T["feat_club"]), ("sea", T["feat_sea"]),
        ]
        feat_cols = st.columns(4)
        for i, (fkey, flabel) in enumerate(feat_items):
            with feat_cols[i % 4]:
                active = fkey in st.session_state.selected_features
                if st.button(flabel, key="feat_" + fkey, use_container_width=True,
                             type="primary" if active else "secondary"):
                    if active:
                        st.session_state.selected_features.remove(fkey)
                    else:
                        st.session_state.selected_features.append(fkey)
                    st.rerun()

        amenity_count = 5 + len(st.session_state.selected_features)

        st.markdown("---")
        predict_btn = st.button(T["calculate"], type="primary", use_container_width=True, key="predict_btn")


    with col_result:
        if predict_btn:
            with st.spinner(T["calculating"]):
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

                input_data["size"] = size
                input_data["bedrooms"] = bedrooms
                input_data["bathrooms"] = bathrooms
                input_data["amenity_count"] = amenity_count
                input_data["images_count"] = 10
                input_data["latitude"] = lat
                input_data["longitude"] = lon
                input_data["property_type"] = selected_ptype
                input_data["governorate"] = selected_gov["en"]
                input_data["district"] = selected_district["en"]
                input_data["compound"] = selected_compound["en"]
                input_data["completion_status"] = "completed"
                input_data["furnished"] = furnished
                input_data["seller_type"] = "Broker"
                input_data["developer_name"] = "Unknown"
                input_data["view"] = "Unknown"
                input_data["finishing_type"] = finishing
                input_data["payment_method"] = "Unknown"
                input_data["town"] = selected_gov["en"]
                input_data["area_per_room"] = size / max(bedrooms, 1)
                input_data["total_rooms"] = bedrooms + bathrooms + living_rooms + kitchens
                input_data["bed_bath_ratio"] = bedrooms / max(bathrooms, 1)
                input_data["amenity_per_room"] = amenity_count / max(bedrooms + bathrooms, 1)
                input_data["images_per_room"] = 10 / max(bedrooms + bathrooms, 1)
                input_data["lat_x_lon"] = lat * lon
                input_data["distance_to_cairo"] = 0
                input_data["distance_to_coast"] = 0
                input_data["distance_cairo_sq"] = 0
                input_data["is_coastal"] = 0
                input_data["is_cairo_center"] = 0
                input_data["is_high_end"] = 1 if selected_ptype in ["Villa", "Penthouse"] else 0
                input_data["is_luxury"] = 1 if selected_ptype in ["Villa", "Penthouse", "Townhouse"] else 0
                input_data["is_compound"] = 0 if selected_compound["en"] == "No Compound" else 1
                input_data["is_premium"] = 0
                input_data["is_featured"] = 0
                input_data["walk_score"] = 50
                input_data["transit_score"] = 50
                input_data["amenity_score"] = amenity_count / 20
                input_data["floor_level"] = floor
                input_data["year_built"] = 2024
                input_data["has_premium_info"] = 0

                X = build_features(input_data, metadata["features"], metadata["cat_features"])
                result = predict_with_confidence(model, X, metadata["features"], metadata["cat_features"])
                price = result["price"]
                ppm2 = price / size

                st.session_state.current_prediction = {
                    "governorate": selected_gov["en"],
                    "district": selected_district["en"],
                    "property_type": selected_ptype,
                    "size": size, "bedrooms": bedrooms, "bathrooms": bathrooms,
                    "price": price, "ppm2": ppm2,
                }

            price_html = (
                '<div class="price-card">'
                '<div class="price-label">' + T["result_title"] + '</div>'
                '<div class="price-value">' + f'{price:,.0f}' + '</div>'
                '<div class="price-currency">' + T["currency"] + '</div>'
                '<div class="price-per-m2">' + T["per_sqm"] + ': ' + f'{ppm2:,.0f}' + '</div>'
                '</div>'
            )
            st.markdown(price_html, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric(T["price_range"], f'{result["price_low"]/1e6:.1f}M - {result["price_high"]/1e6:.1f}M')
            m2.metric(T["confidence"], f'{result["confidence"]*100:.0f}%')

            market_median = df[
                (df["governorate"] == selected_gov["en"]) &
                (df["property_type"] == selected_ptype)
            ]["price"].median()

            if pd.notna(market_median):
                diff = ((price - market_median) / market_median) * 100
                if diff > 10:
                    vs_label = f'{diff:.0f}% ' + T["above_market"]
                elif diff < -10:
                    vs_label = f'{abs(diff):.0f}% ' + T["below_market"]
                else:
                    vs_label = T["at_market"]
                m3.metric(T["vs_market"], vs_label)


            st.markdown("---")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button(T["save"], use_container_width=True, key="save_pred"):
                    st.session_state.favorites.append(st.session_state.current_prediction)
                    st.success(T["saved"])
            with b2:
                wa_html = (
                    '<a href="https://wa.me/201001234567" target="_blank" '
                    'style="text-decoration:none;display:block;">'
                    '<button style="width:100%;padding:12px;background:#25D366;'
                    'color:white;border:none;border-radius:8px;font-weight:700;'
                    'font-size:14px;cursor:pointer;">' + T["whatsapp"] + '</button></a>'
                )
                st.markdown(wa_html, unsafe_allow_html=True)
            with b3:
                primary_color = get_theme(dark)["primary"]
                call_html = (
                    '<a href="tel:+201001234567" style="text-decoration:none;display:block;">'
                    '<button style="width:100%;padding:12px;background:' + primary_color + ';'
                    'color:white;border:none;border-radius:8px;font-weight:700;'
                    'font-size:14px;cursor:pointer;">' + T["call"] + '</button></a>'
                )
                st.markdown(call_html, unsafe_allow_html=True)
        else:
            empty_html = (
                '<div class="empty-state">'
                '<div class="empty-title">' + T["hero_title"] + '</div>'
                '<div class="empty-desc">' + T["hero_sub"] + '</div>'
                '</div>'
            )
            st.markdown(empty_html, unsafe_allow_html=True)


# ═══ TAB 2: MARKET ANALYSIS ═══
with tab2:
    st.markdown('<div class="section-title">' + T["tab_market"] + '</div>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["stat_listings"], f'{len(df):,}')
    c2.metric(T["stat_gov"], str(n_gov))
    c3.metric("Avg Price", f'{df["price"].mean()/1e6:.1f}M')
    c4.metric("Median Price", f'{df["price"].median()/1e6:.1f}M')

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        gov_counts = df["governorate"].value_counts().head(6)
        fig = px.pie(values=gov_counts.values, names=gov_counts.index,
                     title="Listings by Governorate")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        ptype_counts = df["property_type"].value_counts().head(6)
        fig = px.bar(x=ptype_counts.values, y=ptype_counts.index, orientation="h",
                     title="Property Types",
                     color_discrete_sequence=[get_theme(dark)["primary"]])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    price_data = df[df["price"] < df["price"].quantile(0.95)]
    fig = px.histogram(price_data, x="price", nbins=50,
                       title="Price Distribution",
                       color_discrete_sequence=[get_theme(dark)["primary"]])
    st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 3: MORTGAGE ═══
with tab3:
    st.markdown('<div class="section-title">' + T["tab_mortgage"] + '</div>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        loan = st.number_input(T["mortgage_loan"], 100000, 100000000, 2000000, 100000, key="m_loan")
        rate = st.number_input(T["mortgage_rate"], 1.0, 30.0, 12.0, 0.25, key="m_rate")
        years = st.number_input(T["mortgage_years"], 1, 30, 10, key="m_years")

    monthly_rate = rate / 100 / 12
    n_payments = years * 12

    if monthly_rate > 0:
        monthly = loan * monthly_rate * (1 + monthly_rate) ** n_payments / ((1 + monthly_rate) ** n_payments - 1)
    else:
        monthly = loan / n_payments

    total = monthly * n_payments
    interest = total - loan

    with c2:
        m1, m2, m3 = st.columns(3)
        m1.metric(T["mortgage_monthly"], f'{monthly:,.0f}')
        m2.metric(T["mortgage_total"], f'{total:,.0f}')
        m3.metric(T["mortgage_interest"], f'{interest:,.0f}')

# ═══ TAB 4: FAVORITES ═══
with tab4:
    st.markdown('<div class="section-title">' + T["tab_favorites"] + '</div>', unsafe_allow_html=True)
    st.markdown("")

    if not st.session_state.favorites:
        empty_html = (
            '<div class="empty-state">'
            '<div class="empty-title">' + T["empty_title"] + '</div>'
            '<div class="empty-desc">' + T["empty_desc"] + '</div>'
            '</div>'
        )
        st.markdown(empty_html, unsafe_allow_html=True)
    else:
        for i, fav in enumerate(st.session_state.favorites):
            c1, c2 = st.columns([5, 1])
            with c1:
                fav_html = (
                    '<div class="fav-item">'
                    '<div class="fav-title">' + str(fav.get("property_type", "")) + " in " + str(fav.get("district", "")) + '</div>'
                    '<div class="fav-detail">' + f'{fav.get("size", 0):.0f} sqm | {fav.get("bedrooms", 0)} beds | {fav.get("bathrooms", 0)} baths' + '</div>'
                    '<div class="fav-price">' + f'{fav.get("price", 0):,.0f}' + " " + T["currency"] + '</div>'
                    '</div>'
                )
                st.markdown(fav_html, unsafe_allow_html=True)
            with c2:
                if st.button("X", key="del_" + str(i), use_container_width=True):
                    st.session_state.favorites.pop(i)
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ═══ FOOTER ═══
footer_html = (
    '<div class="footer">'
    '<div class="footer-brand">' + T["brand_prefix"] + " " + T["brand_suffix"] + '</div>'
    '<div>' + T["footer_tagline"] + '</div>'
    '<div style="margin-top:16px;font-size:12px;opacity:0.7;">'
    + f'{training["n_total"]:,}' + " listings | " + str(n_gov) + " governorates | R2 = " + f'{metrics["r2"]:.4f}'
    + '</div>'
    '<div style="margin-top:8px;font-size:11px;opacity:0.5;">'
    '2026 Egypt Real Estate AI - ' + T["footer_rights"] +
    '</div>'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
