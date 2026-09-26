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

from location_selector import render_hierarchical_selector
from theme import get_global_css, get_hero_html, get_section_header_html, get_step_header_html
from neighborhood_insights import render_neighborhood_insights
from popular_areas import render_popular_areas
from property_types import render_property_types, get_coefficient, get_note
from dark_theme import get_css as get_theme_css
from featured_properties import render_featured_properties
from filters_chips import render_quick_filters
from auth_login import render_auth
from saved_searches import render_save_search_button, render_saved_searches
from discover_section import render_discover_section
from nearby_transport import render_transport
from safety_schools import render_safety_schools
from mortgage_calculator import render_mortgage_calculator
from save_favorites import render_save_button, render_saved_list
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
    calculate_roi, recommend_similar_properties,
)
# Translations
from translations import TRANSLATIONS


def _translate_feat_name(name, L, FEATURE_MAP, lang='ar'):
    """Translate a feature name from the model to the current language."""
    raw = name.replace('num__','').replace('cat__','')
    if raw.startswith('city_'):
        val = raw.replace('city_','').replace('_',' ').title()
        if lang == 'ar':
            val = CITY_NAMES.get(val, val)
            prefix = L.get('feat_city','City')
        else:
            prefix = 'City'
        return prefix + ': ' + val
    if raw.startswith('district_'):
        val = raw.replace('district_','').replace('_',' ').title()
        if lang == 'ar':
            val = CITY_NAMES.get(val, val)
            prefix = L.get('feat_district','District')
        else:
            prefix = 'District'
        return prefix + ': ' + val
    if raw.startswith('compound_'):
        val = raw.replace('compound_','').replace('_',' ').title()
        if lang == 'ar':
            val = CITY_NAMES.get(val, val)
            prefix = L.get('feat_compound','Compound')
        else:
            prefix = 'Compound'
        return prefix + ': ' + val
    clean = raw.replace('_',' ').title()
    key = FEATURE_MAP.get(clean.lower(), '')
    return L.get(key, clean)

# Load place name translations from JSON
import json as _json
_CITY_MAP_PATH = Path(__file__).resolve().parent / "data" / "place_translations.json"
try:
    CITY_NAMES = _json.loads(_CITY_MAP_PATH.read_text(encoding='utf-8'))
    # Alias للحفاظ على التوافق
    CITY_NAMES.update({
        'Al Daqahlya': 'الدقهلية',
        'New Cairo City': 'القاهرة الجديدة',
    })
except Exception as _e:
    CITY_NAMES = {'Cairo': 'القاهرة', 'Giza': 'الجيزة', 'Alexandria': 'الإسكندرية'}

# Feature name translation map
FEATURE_MAP = {
    'area': 'feat_area', 'bedrooms': 'feat_bedrooms', 'bathrooms': 'feat_bathrooms',
    'size': 'feat_size', 'amenity count': 'feat_amenity', 'amenity study': 'feat_study',
    'distance to cairo': 'feat_dist_cairo', 'title length': 'feat_title_len',
    'title word count': 'feat_word_count', 'city': 'feat_city', 'district': 'feat_district',
    'gps': 'feat_gps', 'compound': 'feat_compound', 'age': 'feat_age',
    'area per bedroom': 'feat_area_bed',
    'geo cluster': 'geo_cluster', 'rooms total': 'rooms_total',
    'latitude': 'latitude', 'longitude': 'longitude',
    'amenity count': 'feat_amenity', 'amenity study': 'feat_study',
}


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
    initial_sidebar_state="expanded",
)


@st.cache_resource
def _load():
    return load_artifacts()

try:
    model, metadata, mappings = _load()
    categories = get_category_values(mappings)
except Exception as e:
    st.error(f"Model loading error: {e}")
    st.stop()


# ============================================================
# DARK MODE + LANGUAGE SELECTOR
# ============================================================
top_cols = st.columns([1, 1, 1, 1, 1, 1])

with top_cols[4]:
    dark_mode = st.toggle(
        "🌙 Dark",
        value=False,
        key="dark_mode_toggle",
        help="Dark mode / الوضع الليلي",
    )

with top_cols[5]:
    lang_option = st.selectbox(
        "Language / اللغة",
        ["English", "العربية"],
        key="lang_selector",
        label_visibility="collapsed",
    )

lang = "ar" if "العربية" in lang_option else "en"
L = TRANSLATIONS[lang]
is_rtl = (lang == "ar")

# ═══════════════════════════════════════════════════════
# GLOBAL CSS — Light/Dark theme
# ═══════════════════════════════════════════════════════
st.markdown(get_theme_css(dark=dark_mode, lang=lang), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SIDEBAR — Auth + Saved Properties
# ═══════════════════════════════════════════════════════
with st.sidebar:
    # ─── Auth Section ───
    _auth_title = "👤 الحساب" if lang == "ar" else "👤 Account"
    st.markdown(f"### {_auth_title}")

    try:
        _auth_result = render_auth(lang=lang)
        if _auth_result and _auth_result[0]:
            _authenticator, _cfg = _auth_result
            _name = st.session_state.get("name", "")
            _auth_status = st.session_state.get("authentication_status", False)

            if _auth_status:
                _welcome = f"أهلاً، {_name}" if lang == "ar" else f"Welcome, {_name}"
                st.success(f"✅ {_welcome}")
                _authenticator.logout(
                    "🚪 خروج" if lang == "ar" else "🚪 Logout",
                    location="sidebar",
                )
            elif _auth_status is False:
                st.error("❌ اسم المستخدم أو كلمة المرور غلط" if lang == "ar"
                        else "❌ Wrong username or password")
            else:
                st.caption("سجل دخول لحفظ العقارات" if lang == "ar"
                          else "Login to save properties")
    except Exception as _e:
        st.caption("ℹ️ " + ("الحساب مش متاح مؤقتاً" if lang == "ar"
                           else "Account temporarily unavailable"))

    st.markdown("---")

    # ─── Saved Properties ───
    try:
        render_saved_list(lang=lang)
    except Exception:
        pass

    # ─── Saved Searches ───
    try:
        render_saved_searches(lang=lang)
    except Exception:
        pass

# ============================================================
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

hero_html = get_hero_html(
    lang=lang,
    accuracy=r2_str,
    error=mape_str + "%",
    cities=len(categories["city"]),
    listings=int(metadata['training_info']['n_total']),
)
st.markdown(hero_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# FEATURED PROPERTIES (like Property Finder)
# ═══════════════════════════════════════════════════════
render_featured_properties(lang=lang)


# ═══════════════════════════════════════════════════════
# POPULAR AREAS (like Property Finder)
# ═══════════════════════════════════════════════════════
render_popular_areas(lang=lang)

# ═══════════════════════════════════════════════════════
# PROPERTY TYPES (like Property Finder)
# ═══════════════════════════════════════════════════════
render_property_types(lang=lang)


# ═══════════════════════════════════════════════════════
# QUICK FILTERS (like Property Finder)
# ═══════════════════════════════════════════════════════
render_quick_filters(lang=lang)


# ============================================================
# 2-COLUMN: FORM (left) + PREVIEW (right)
# ============================================================
col_left, col_right = st.columns([6, 4], gap="large")

with col_left:
    # STEP 1: LOCATION
    step1_title = get_step_header_html(1, "📍", L['step1'], "اختار المحافظة والمدينة والحي" if lang=="ar" else "Choose governorate, city, district")
    st.markdown('<div class="form-card">' + step1_title, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════
    # 5-LEVEL HIERARCHICAL SELECTOR
    # ═══════════════════════════════════════════════
    _loc = render_hierarchical_selector(lang=lang)
    if _loc is None:
        st.stop()

    city = _loc["city"]
    district = _loc["district"]
    compound = _loc["compound"]
    _gov_selected = _loc["governorate_en"]
    _gov_status = _loc["data_status"]

    # ── Fallbacks لو المستخدم اختار "الكل" ──
    if city == "all":
        # نختار أول مدينة حقيقية في المحافظة دي
        import json as _json
        _h = _json.loads((Path(__file__).resolve().parent / "data" / "egypt_hierarchy.json").read_text(encoding="utf-8"))
        for _g in _h["governorates"]:
            if _g["en"] == _gov_selected:
                _real = list({c["source_city"] for c in _g["cities_with_data"]})
                city = _real[0] if _real else "Cairo"
                break
    if district == "all":
        import json as _json
        _h = _json.loads((Path(__file__).resolve().parent / "data" / "egypt_hierarchy.json").read_text(encoding="utf-8"))
        for _g in _h["governorates"]:
            if _g["en"] == _gov_selected:
                _d = [c for c in _g["cities_with_data"] if c["source_city"] == city]
                district = _d[0]["en"] if _d else "New Cairo City"
                break

    # Warning for sparse data
    if _gov_status in ("low", "minimal"):
        _warn_txt = (
            f"⚠️ البيانات المتاحة لمحافظة **{_loc['governorate_ar']}** محدودة — التوقعات تقريبية."
            if lang == "ar"
            else f"⚠️ Data for **{_loc['governorate_en']}** is limited — estimates are approximate."
        )
        st.warning(_warn_txt)

    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 2: SIZE & ROOMS
    step2_title = get_step_header_html(2, "📐", L['step2'], "المساحة وعدد الغرف" if lang=="ar" else "Area and rooms count")
    st.markdown('<div class="form-card">' + step2_title, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # ROW 1: Area + Bedrooms + Bathrooms (expanded)
    # ═══════════════════════════════════════════════════════
    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.slider(L["area"], 20, 600, 150, 5, key="s_area")
    with c2:
        bedrooms = st.selectbox(
            L["bedrooms"],
            ["Studio", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            index=3, key="s_beds",
        )
    with c3:
        bathrooms = st.slider(L["bathrooms"], 1, 8, 2, key="s_baths")

    # ═══════════════════════════════════════════════════════
    # ROW 2: Reception + Kitchen + Floor (like Property Finder)
    # ═══════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        reception = st.selectbox(
            L.get("reception", "Reception / صالة"),
            ["1", "2", "3", "4", "5"],
            index=0, key="s_reception",
            help="عدد الصالات / الريسبشن" if lang == "ar" else "Number of reception rooms",
        )
    with d2:
        kitchen = st.selectbox(
            L.get("kitchen", "Kitchen / مطبخ"),
            ["1", "2", "3"],
            index=0, key="s_kitchen",
            help="عدد المطابخ" if lang == "ar" else "Number of kitchens",
        )
    with d3:
        floor = st.selectbox(
            L.get("floor", "Floor / الدور"),
            ["Basement", "Ground", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
            index=2, key="s_floor",
            help="الطابق" if lang == "ar" else "Floor number",
        )

    # ═══════════════════════════════════════════════════════
    # ROW 3: Property Type + Finishing + Furnished (like Aqarmap)
    # ═══════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    with e1:
        prop_type = st.selectbox(
            L.get("prop_type", "Property Type / نوع العقار"),
            [
                ("Apartment", "شقة"),
                ("Villa", "فيلا"),
                ("Duplex", "دوبلكس"),
                ("Penthouse", "بنتهاوس"),
                ("Townhouse", "تاون هاوس"),
                ("Studio", "ستوديو"),
                ("Chalet", "شاليه"),
            ],
            format_func=lambda x: x[1] if lang == "ar" else x[0],
            index=0, key="s_ptype",
        )
    with e2:
        finishing = st.selectbox(
            L.get("finishing", "Finishing / التشطيب"),
            [
                ("N/A", "غير محدد"),
                ("Semi-Finished", "نصف تشطيب"),
                ("Finished", "تشطيب عادي"),
                ("Lux", "لوكس"),
                ("Super Lux", "سوبر لوكس"),
                ("Extra Super Lux", "إكسترا سوبر لوكس"),
            ],
            format_func=lambda x: x[1] if lang == "ar" else x[0],
            index=4, key="s_finish",
        )
    with e3:
        furnished = st.selectbox(
            L.get("furnished", "Furnished / التأثيث"),
            [
                ("Unfurnished", "غير مفروش"),
                ("Semi-Furnished", "نص مفروش"),
                ("Fully Furnished", "مفروش بالكامل"),
            ],
            format_func=lambda x: x[1] if lang == "ar" else x[0],
            index=0, key="s_furnish",
        )

    # ═══════════════════════════════════════════════════════
    # ROW 4: Year Built + Parking + View
    # ═══════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        year_built = st.slider(
            L.get("year_built", "Year Built / سنة البناء"),
            1950, 2026, 2020, 1, key="s_year",
        )
    with f2:
        parking = st.selectbox(
            L.get("parking", "Parking / مواقف"),
            ["0", "1", "2", "3", "4", "5"],
            index=1, key="s_parking",
            help="عدد مواقف السيارات" if lang == "ar" else "Number of parking spaces",
        )
    with f3:
        view = st.selectbox(
            L.get("view", "View / الإطلالة"),
            [
                ("Street", "شارع"),
                ("Garden", "حديقة"),
                ("Pool", "حمام سباحة"),
                ("Sea", "بحر"),
                ("Nile", "النيل"),
                ("Open", "مفتوحة"),
                ("Landmark", "معلم سياحي"),
            ],
            format_func=lambda x: x[1] if lang == "ar" else x[0],
            index=0, key="s_view",
        )

    # ── For model compatibility ──
    _bedrooms_num = "1" if bedrooms == "Studio" else str(bedrooms)
    _prop_type_en = prop_type[0]
    _finishing_en = finishing[0]
    _furnished_en = furnished[0]
    _view_en = view[0]


    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 3: AMENITIES
    step3_title = get_step_header_html(3, "✨", L['step3'], "اختار المميزات المتاحة" if lang=="ar" else "Select available amenities")
    st.markdown('<div class="form-card">' + step3_title, unsafe_allow_html=True)

    AMENITY_UI = {
        L["am_ba"]: "BA", L["am_bw"]: "BW", L["am_cp"]: "CP",
        L["am_pg"]: "PG", L["am_sp"]: "SP", L["am_se"]: "SE",
        L["am_ac"]: "AC", L["am_bk"]: "BK", L["am_mr"]: "MR",
        L["am_st"]: "ST", L["am_co"]: "CO", L["am_gy"]: "GY",
    }
    selected_amenities = []
    cols = st.columns(3)
    for i, (label, code) in enumerate(AMENITY_UI.items()):
        with cols[i % 3]:
            if st.checkbox(label, value=(code in ["BA", "SE"]), key=f"am_{code}"):
                selected_amenities.append(code)

    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 4: DESCRIPTION
    step4_title = get_step_header_html(4, "📝", L['step4'], "تفاصيل إضافية (اختياري)" if lang=="ar" else "Additional details (optional)")
    st.markdown('<div class="form-card">' + step4_title, unsafe_allow_html=True)

    description = st.text_area(
        L["description"],
        placeholder=L["desc_placeholder"],
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
    bd_text = L["studio"] if bedrooms == "studio" else f"{bedrooms} {L['br']}"
    compound_text = compound if compound != "None" else "—"
    amenity_count = len(selected_amenities)

    # اسم نوع العقار
    _ptype_label = prop_type[1] if lang == "ar" else prop_type[0]
    _finish_label = finishing[1] if lang == "ar" else finishing[0]
    _furnish_label = furnished[1] if lang == "ar" else furnished[0]
    _view_label = view[1] if lang == "ar" else view[0]
    _floor_label = floor if floor not in ("Ground", "Basement") else ("أرضي" if floor == "Ground" and lang == "ar" else "بدروم" if lang == "ar" else floor)

    # ═══════════════════════════════════════════════════════
    # Modern Live Preview Card (Property Finder style)
    # ═══════════════════════════════════════════════════════
    preview_html = (
        '<div style="background:white;border:1px solid #e5e7eb;'
        'border-radius:20px;overflow:hidden;'
        'box-shadow:0 8px 32px rgba(99,102,241,0.10);">'

        # ── Header Image ──
        '<div style="height:130px;'
        'background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:52px;position:relative;">🏢'
        '<div style="position:absolute;top:12px;right:12px;'
        'background:rgba(255,255,255,0.28);backdrop-filter:blur(10px);'
        'padding:5px 12px;border-radius:100px;'
        'font-size:10px;font-weight:800;color:white;letter-spacing:0.5px;">'
        + L['live_preview'] + '</div></div>'

        # ── Body ──
        '<div style="padding:18px;">'

        # Title
        '<div style="font-size:16px;font-weight:900;color:#1f2937;'
        'margin-bottom:4px;">'
        + _ptype_label + ' · ' + f'{area}' + ' م² · ' + bd_text + '</div>'

        # Location
        '<div style="font-size:11px;color:#6b7280;font-weight:600;'
        'margin-bottom:14px;">📍 '
        + (CITY_NAMES.get(city, city) if lang == 'ar' else city)
        + ' → '
        + (CITY_NAMES.get(district, district) if lang == 'ar' else district) + '</div>'

        # ── Stats Grid (3 core) ──
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);'
        'gap:8px;margin-bottom:14px;">'
        '<div style="background:#eef2ff;border-radius:10px;padding:9px 4px;text-align:center;">'
        '<div style="font-size:17px;font-weight:900;color:#6366f1;">' + f'{bathrooms}' + '</div>'
        '<div style="font-size:9px;color:#6b7280;font-weight:700;'
        'text-transform:uppercase;margin-top:2px;">' + L['bath_label'] + '</div></div>'

        '<div style="background:#f0fdf4;border-radius:10px;padding:9px 4px;text-align:center;">'
        '<div style="font-size:17px;font-weight:900;color:#10b981;">' + f'{amenity_count}' + '</div>'
        '<div style="font-size:9px;color:#6b7280;font-weight:700;'
        'text-transform:uppercase;margin-top:2px;">' + L['amen_label'] + '</div></div>'

        '<div style="background:#fff7ed;border-radius:10px;padding:9px 4px;text-align:center;">'
        '<div style="font-size:12px;font-weight:900;color:#f59e0b;'
        'line-height:1.3;overflow:hidden;text-overflow:ellipsis;'
        'white-space:nowrap;padding:0 2px;">' + compound_text + '</div>'
        '<div style="font-size:9px;color:#6b7280;font-weight:700;'
        'text-transform:uppercase;margin-top:2px;">' + L['comp_label'] + '</div></div>'
        '</div>'

        # ── Extra details ──
        '<div style="border-top:1px solid #f3f4f6;padding-top:12px;">'
        '<div style="font-size:10px;font-weight:800;color:#9ca3af;'
        'text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">'
        + ('تفاصيل إضافية' if lang == 'ar' else 'EXTRA DETAILS') + '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;'
        'font-size:11px;color:#1f2937;">'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">🛋️ ' + L['reception'] + '</span>'
        '<b>' + reception + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">🍳 ' + L['kitchen'] + '</span>'
        '<b>' + kitchen + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">🏢 ' + L['floor'] + '</span>'
        '<b>' + _floor_label + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">🚗 ' + L['parking'] + '</span>'
        '<b>' + parking + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">📅 ' + L['year_built'] + '</span>'
        '<b>' + str(year_built) + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">🛋️ ' + L['furnished'] + '</span>'
        '<b>' + _furnish_label + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">🎨 ' + L['finishing'] + '</span>'
        '<b>' + _finish_label + '</b></div>'
        '<div style="display:flex;justify-content:space-between;">'
        '<span style="color:#6b7280;">👁️ ' + L['view'] + '</span>'
        '<b>' + _view_label + '</b></div>'
        '</div></div>'
        '</div></div>'
    )
    st.markdown(preview_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SAVE SEARCH + PREDICT BUTTONS
    # ═══════════════════════════════════════════════════════
    _bs1, _bs2 = st.columns([1, 3])
    with _bs1:
        try:
            _search_filters = {
                "governorate": _loc.get("governorate_ar" if lang == "ar" else "governorate_en", ""),
                "district": district,
                "bedrooms": bedrooms,
                "price_range": f"{area} m²",
            }
            render_save_search_button(_search_filters, lang=lang)
        except Exception as _e:
            pass
    with _bs2:
        predict_btn = st.button("🔮  " + L["cta"], type="primary", use_container_width=True)
if predict_btn:
    st.session_state["show_result"] = True



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


if st.session_state.get("show_result", False):
    errors = validate_input(area, bedrooms, bathrooms, city, district, compound)
    if errors:
        st.error("WARNING: " + " | ".join(errors))
    else:
        result = predict_with_confidence(model, input_features, m["mape"])
        _base_price = result["price"]

        # ═══════════════════════════════════════════════════════
        # PROPERTY TYPE COEFFICIENT
        # ═══════════════════════════════════════════════════════
        _pt_key = prop_type[0] if isinstance(prop_type, tuple) else "Apartment"
        _coef = get_coefficient(_pt_key)
        price = _base_price * _coef
        result["lower_bound"] = result["lower_bound"] * _coef
        result["upper_bound"] = result["upper_bound"] * _coef
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
        st.markdown("## 📊 " + L["result_title"])

        res_left, res_right = st.columns([5, 5], gap="large")

        with res_left:
            price_html = (
                '<div class="price-hero">'
                '<div class="price-label">' + L['est_value'] + '</div>'
                '<div class="price-value">' + f'{price/1_000_000:.2f}M' + '</div>'
                '<div class="price-egp">' + f'{price:,.0f}' + ' EGP</div>'
                '<div style="font-size:0.72rem;color:#6b7280;margin-top:0.35rem;">' + L['range'] + '</div>'
                '<div class="price-range-bar"><div class="price-range-fill"></div></div>'
                '<div class="price-range-labels">'
                '<span>' + format_price(result['lower_bound']) + '</span>'
                '<span>' + format_price(result['upper_bound']) + '</span>'
                '</div></div>'
            )
            st.markdown(price_html, unsafe_allow_html=True)

            # ═══ Transparency note for non-Apartment types ═══
            if _pt_key != "Apartment":
                _note = get_note(_pt_key, lang=lang)
                _warn = (
                    f"ℹ️ **{_note}**: تقدير **{_pt_key}** مبني على بيانات الشقق + معامل سوقي ×{_coef}. للتقييم الدقيق، اتصل بمثمّن عقاري."
                    if lang == "ar"
                    else f"ℹ️ **{_note}**: {_pt_key} estimate is based on Apartment data + market coefficient ×{_coef}. For precise valuation, consult a certified appraiser."
                )
                st.info(_warn)

            monthly_rate = 0.10 / 12
            n_payments = 20 * 12
            down_payment = price * 0.20
            loan_amount = price - down_payment
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -n_payments)

            monthly_html = (
                '<div class="monthly-card">'
                '<div class="monthly-title">' + L['monthly_title'] + '</div>'
                '<div class="monthly-value">' + f'{monthly_payment:,.0f}' + ' EGP</div>'
                '<div class="monthly-detail">' + L['monthly_detail'] + '</div>'
                '</div>'
            )
            st.markdown(monthly_html, unsafe_allow_html=True)

            # Save property button
            st.markdown("<br>", unsafe_allow_html=True)
            _save_data = {
                "area": int(area), "bedrooms": str(bedrooms), "bathrooms": int(bathrooms),
                "city": city, "district": district, "compound": compound,
                "price": float(price),
                "lower": float(result['lower_bound']),
                "upper": float(result['upper_bound']),
            }
            render_save_button(_save_data, lang=lang)

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
                        "📄 " + L["pdf_btn"], data=pdf_buf,
                        file_name="property_report.pdf",
                        mime="application/pdf", use_container_width=True,
                    )
                except Exception:
                    pass

            share_text = L["share_text"].format(price=f"{price:,.0f}", area=area, district=district, city=city)
            share_url = "https://wa.me/?text=" + share_text.replace(' ', '%20')
            share_html = (
                '<a href="' + share_url + '" target="_blank" style="display:block;width:100%;text-align:center;'
                'background:#25D366;color:white;padding:0.85rem 1.5rem;border-radius:12px;font-weight:800;'
                'text-decoration:none;font-size:0.95rem;margin-top:0.5rem;">'
                '' + L['share_wa'] + '</a>'
            )
            st.markdown(share_html, unsafe_allow_html=True)

        with res_right:
            district_ppm = mappings['price_mappings']['district_price_per_sqm'].get(district, 0)
            diff_pct = ((ppm - district_ppm) / district_ppm * 100) if district_ppm else 0
            arrow = "🟢" if diff_pct >= 0 else "🔴"

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f'{ppm:,.0f}' + '</div><div class="metric-label">' + L['ppm'] + '</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f'{district_ppm:,.0f}' + '</div><div class="metric-label">' + L['dist_avg'] + '</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f'{diff_pct:+.1f}' + '%</div><div class="metric-label">' + L['vs_dist'] + '</div></div>', unsafe_allow_html=True)

            city_growth = {"Cairo": 15.2, "Giza": 17.2, "Alexandria": 13.1, "Red Sea": 12.0, "North Coast": 14.5, "Suez": 16.0}
            growth = city_growth.get(city, 15.0)
            history_html = (
                '<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:12px;padding:0.85rem;margin-top:0.75rem;">'
                '<div style="font-weight:800;color:#78350f;font-size:0.8rem;">' + L['trend_title'] + '</div>'
                '<div style="color:#92400e;font-size:0.72rem;margin-top:0.15rem;">' + L['trend_text'].format(city=(CITY_NAMES.get(city, city) if lang == 'ar' else city), g=f'{growth:.1f}') + '</div>'
                '<div style="font-size:1.3rem;font-weight:900;color:#78350f;margin-top:0.35rem;">+' + f'{growth:.1f}' + '%</div>'
                '</div>'
            )
            st.markdown(history_html, unsafe_allow_html=True)



        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 🔍 " + L["dive"])

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "🧠 " + L["tab1"], "🗺️ " + L["tab2"], "🏘️ " + L["tab3"],
            "⚖️ " + L["tab4"], "💰 " + L["tab5"], "📈 " + L["tab6"], "📍 " + L["tab7"],
            "🏘️ " + L["tab8"], "🏦 " + L["tab9"]
        ])

        with tab1:
            st.caption(L["t1_caption"])
            try:
                prep = model.named_steps['prep']
                X_t = prep.transform(input_features)
                feat_names = prep.get_feature_names_out()
                explainer = shap.TreeExplainer(model.named_steps['model'])
                sv = np.array(explainer.shap_values(X_t)).flatten()
                top_n = 10
                idx = np.argsort(np.abs(sv))[-top_n:][::-1]
                clean_names = [_translate_feat_name(feat_names[i], L, FEATURE_MAP, lang=lang) for i in idx]
                colors = ['#10b981' if v > 0 else '#ef4444' for v in sv[idx]]
                fig = go.Figure(go.Bar(
                    x=sv[idx], y=clean_names, orientation='h',
                    marker_color=colors,
                    text=[f"{v:+.3f}" for v in sv[idx]], textposition='outside',
                ))
                fig.update_layout(height=400, margin=dict(l=10, r=40, t=20, b=20),
                                   xaxis_title=L["impact_price"], showlegend=False, plot_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
                st.caption(L["t1_green"])
            except Exception as e:
                st.error(f"SHAP error: {e}")

        with tab2:
            st.markdown(f"#### {L['t2_title']}")
            price_data = mappings['price_mappings']['district_price_per_sqm']
            ppm_series = pd.Series(price_data).sort_values(ascending=True).tail(20)
            if lang == 'ar':
                ppm_series.index = [(CITY_NAMES.get(x, x) if lang == 'ar' else x) for x in ppm_series.index]
            fig = go.Figure(go.Bar(
                x=ppm_series.values, y=ppm_series.index, orientation='h',
                marker=dict(color=ppm_series.values, colorscale='RdYlGn_r', showscale=False),
                text=[f"{v:,.0f}" for v in ppm_series.values], textposition='outside',
            ))
            fig.update_layout(height=600, margin=dict(l=10, r=60, t=20, b=20),
                              xaxis_title=L["t2_xlabel"])
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.caption(L["t3_caption"])
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
                    st.caption(L["t3_found"].format(n=len(recs)))
                    for i, r in enumerate(recs, 1):
                        sim_pct = r['similarity'] * 100
                        bd = L["studio"] if r.get('is_studio') == 1 else f"{r['bedrooms_clean']} {L['br']}"
                        card_html = (
                            '<div class="sim-card">'
                            '<div style="display:flex;justify-content:space-between;align-items:center;">'
                            '<div>'
                            '<b style="color:#6366f1;">#' + str(i) + '</b> '
                            '<b>' + f"{r['area_value']:.0f}" + (' م² | ' if lang == 'ar' else ' m2 | ') + bd + '</b>'
                            '<div style="color:#6b7280;font-size:0.82rem;margin-top:0.2rem;">' + (CITY_NAMES.get(r['city'], r['city']) if lang == 'ar' else r['city']) + ' - ' + (CITY_NAMES.get(r['district'], r['district']) if lang == 'ar' else r['district']) + '</div>'
                            '<div style="margin-top:0.3rem;"><span class="sim-match">' + f'{sim_pct:.0f}' + L['t3_match'] + '</span></div>'
                            '</div>'
                            '<div style="text-align:right;">'
                            '<div style="font-size:1.3rem;font-weight:800;color:#10b981;">' + f"{r['predicted_price']/1e6:.2f}" + (' مليون' if lang == 'ar' else 'M') + '</div>'
                            '<div style="font-size:0.68rem;color:#9ca3af;">EGP</div>'
                            '</div></div></div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Recommendation error: {e}")

        with tab4:
            st.caption(L["t4_caption"])
            colA, colB = st.columns(2)
            with colA:
                st.markdown(f"**{L['t4_a']}**")
                _area_unit = ' م²<br>' if lang == 'ar' else ' m2<br>'
                _city_ar = CITY_NAMES.get(city, city) if lang == 'ar' else city
                _dist_ar = CITY_NAMES.get(district, district) if lang == 'ar' else district
                a_html = (
                    '<div class="metric-card">'
                    '<div class="metric-value" style="color:#10b981;">' + f'{price:,.0f}' + ' EGP</div>'
                    '<div style="margin-top:0.5rem;font-size:0.82rem;">'
                    + f'{L["t4_area"]}: ' + f'{area}' + _area_unit
                    + f'{L["bedrooms"]}: ' + str(bedrooms) + '<br>'
                    + f'{L["bathrooms"]}: ' + str(bathrooms) + '<br>'
                    + f'{L["t4_location"]}: ' + _city_ar + ' - ' + _dist_ar + '</div></div>'
                )
                st.markdown(a_html, unsafe_allow_html=True)
            with colB:
                st.markdown(f"**{L['t4_b']}**")
                b_area = st.number_input(L["t4_area"], 40, 500, 200, 5, key="cmp_area")
                b_bedrooms = st.selectbox(L["bedrooms"], ["1","2","3","4","5"], index=3, key="cmp_bed")
                b_bathrooms = st.slider(L["bathrooms"], 1, 5, 3, key="cmp_bath")
                b_district = st.selectbox(L["district"], categories["district"], key="cmp_dist",
                           format_func=lambda x: CITY_NAMES.get(x, x) if lang == "ar" else x)
                b_city = st.selectbox(L["city"], categories["city"], key="cmp_city",
                       format_func=lambda x: CITY_NAMES.get(x, x) if lang == "ar" else x)

                prop_b = {
                    'area': b_area, 'bedrooms': b_bedrooms, 'bathrooms': b_bathrooms,
                    'city': b_city, 'district': b_district,
                    'compound': 'None', 'amenities': [],
                }
                feat_b = build_features(**prop_b, mappings=mappings)
                price_b = predict_with_confidence(model, feat_b, m["mape"])['price']
                _b_city_ar = CITY_NAMES.get(b_city, b_city) if lang == 'ar' else b_city
                _b_dist_ar = CITY_NAMES.get(b_district, b_district) if lang == 'ar' else b_district
                b_html = (
                    '<div class="metric-card">'
                    '<div class="metric-value" style="color:#6366f1;">' + f'{price_b:,.0f}' + ' EGP</div>'
                    '<div style="margin-top:0.5rem;font-size:0.82rem;">'
                    + f'{L["t4_area"]}: ' + f'{b_area}' + _area_unit
                    + f'{L["bedrooms"]}: ' + b_bedrooms + '<br>'
                    + f'{L["bathrooms"]}: ' + str(b_bathrooms) + '<br>'
                    + f'{L["t4_location"]}: ' + _b_city_ar + ' - ' + _b_dist_ar + '</div></div>'
                )
                st.markdown(b_html, unsafe_allow_html=True)

            diff = price - price_b
            if diff < 0:
                st.success(L["t4_cheaper_a"].format(d=f"{abs(diff):,.0f}"))
            else:
                st.info(L["t4_cheaper_b"].format(d=f"{abs(diff):,.0f}"))

        with tab5:
            st.markdown(f"#### {L['t5_title']}")
            roi = calculate_roi(price, years=5)
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['roi_pct']:.0f}" + '%</div><div class="metric-label">' + L["roi_total"] + '</div></div>', unsafe_allow_html=True)
            with i2:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['annualized_roi_pct']:.1f}" + '%</div><div class="metric-label">' + L["roi_annual"] + '</div></div>', unsafe_allow_html=True)
            with i3:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['total_rental_income']/1e6:.2f}" + (' مليون' if lang == 'ar' else 'M') + '</div><div class="metric-label">' + L["roi_rental"] + '</div></div>', unsafe_allow_html=True)
            with i4:
                st.markdown('<div class="metric-card"><div class="metric-value">' + f"{roi['appreciation_gain']/1e6:.2f}" + (' مليون' if lang == 'ar' else 'M') + '</div><div class="metric-label">' + L["roi_appr"] + '</div></div>', unsafe_allow_html=True)

            years_arr = np.arange(6)
            rental = [price * 0.005 * 12 * y / 1e6 for y in years_arr]
            appr = [(price * (1.12 ** y) - price) / 1e6 for y in years_arr]
            fig_roi = go.Figure()
            fig_roi.add_trace(go.Bar(x=years_arr, y=rental, name=L['t5_rental'], marker_color='#10b981'))
            fig_roi.add_trace(go.Bar(x=years_arr, y=appr, name=L['t5_appr'], marker_color='#6366f1'))
            fig_roi.update_layout(barmode='stack', height=320, xaxis_title=L["t5_year"], yaxis_title=L["million_egp"] + "P", plot_bgcolor='white')
            st.plotly_chart(fig_roi, use_container_width=True)

        # ---------- TAB 6: FORECAST ----------
        with tab6:
            st.markdown(f"#### 📈 {L['t6_title']}")
            st.caption(L["t6_caption"])

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
                        name=f"{(CITY_NAMES.get(city_name, city_name) if lang == 'ar' else city_name)} ({L['hist']})",
                        line=dict(color=color, width=1.5),
                        legendgroup=city_name,
                    ))

                    # Forecast line (dashed)
                    forecast_only = preds[preds['ds'] > hist['ds'].max()]
                    fig_ts.add_trace(go.Scatter(
                        x=forecast_only['ds'], y=forecast_only['yhat'],
                        mode='lines',
                        name=f"{(CITY_NAMES.get(city_name, city_name) if lang == 'ar' else city_name)} ({L['forecast_short']})",
                        line=dict(color=color, width=2.5, dash='dash'),
                        legendgroup=city_name,
                    ))

                fig_ts.update_layout(
                    height=550,
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis_title=L["t6_xlabel"],
                    yaxis_title=L["t6_ylabel"],
                    hovermode='x unified',
                    plot_bgcolor='white',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                )

                # Add vertical line for "today"
                fig_ts.add_vline(
                    x=pd.Timestamp('2026-01-01').timestamp() * 1000,
                    line_dash="dot",
                    line_color="gray",
                    annotation_text=L["t6_today"],
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
                        L['t6_current']: f"{data['current_price']:,.0f}",
                        L['t6_forecast']: f"{data['forecast_12m']:,.0f}",
                        L['t6_growth']: f"+{data['growth_12m_pct']:.1f}%",
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
            st.markdown(f"#### 📍 {L['t7_title']}")
            st.caption(L["t7_caption"])

            map_data = _load_map_data()

            if map_data is None:
                st.warning(L["t7_no_data"])
            else:
                import folium
                from streamlit_folium import st_folium

                # Filters
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    cities_in_map = sorted(map_data['city'].unique())
                    selected_cities = st.multiselect(
                        L["t7_filter_city"],
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
                        L["t7_price_range"],
                        min_value=0.0,
                        max_value=float(map_data['price_m'].max()),
                        value=(price_min, price_max),
                        step=0.5,
                        key="map_price_range",
                    )

                with col_c:
                    size_max = int(map_data['size'].max())
                    size_range = st.slider(
                        L["t7_size_range"],
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
                    st.warning("⚠️ " + L["t7_no_match"])
                else:
                    # Color by price
                    def get_color(p):
                        if p < 5: return '#43A047'
                        elif p < 10: return '#FB8C00'
                        else: return '#E53935'

                    # Center map on Egypt
                    map_obj = folium.Map(
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
                            tooltip=f"{(CITY_NAMES.get(row['district'], row['district']) if lang == 'ar' else row['district'])}: {row['price_m']:.2f}M EGP",
                        ).add_to(map_obj)

                    st_folium(map_obj, width=None, height=600, returned_objects=[])

                    # Legend
                    st.markdown("""
                    <div style="background:#f9fafb; padding:1rem; border-radius:10px; margin-top:0.75rem; display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center;">
                        <div><span style="color:#43A047; font-size:1.5rem;">●</span> ' + L["t7_under5"] + '</div>
                        <div><span style="color:#FB8C00; font-size:1.5rem;">●</span> ' + L["t7_5to10"] + '</div>
                        <div><span style="color:#E53935; font-size:1.5rem;">●</span> ' + L["t7_over10"] + '</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Stats per city
                    st.markdown("#### 📊 Properties by City")
                    city_stats = filtered_map.groupby('city').agg({
                        'price_m': ['count', 'mean', 'min', 'max']
                    }).round(2)
                    city_stats.columns = [L['count'], L['avg_price_m'], L['min_m'], L['max_m']]
                    city_stats = city_stats.sort_values(L['count'], ascending=False)
                    st.dataframe(city_stats, use_container_width=True)

        # ---------- TAB 8: NEIGHBORHOOD INSIGHTS ----------
        with tab8:
            st.markdown(f"#### 🏘️ {L['t8_title']}")
            _nb_caption = (
                "معلومات تفصيلية عن الحي — مدارس، مستشفيات، مواصلات، تاريخ الأسعار، والتكاليف"
                if lang == "ar"
                else "Detailed neighborhood info — schools, hospitals, transport, price history, and costs"
            )
            st.caption(_nb_caption)

            # Transport
            try:
                render_transport(district, lang=lang)
            except Exception as _e:
                st.warning(f"Transport: {_e}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Safety & Schools
            try:
                render_safety_schools(district, lang=lang)
            except Exception as _e:
                st.warning(f"Safety: {_e}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Full neighborhood insights
            try:
                render_neighborhood_insights(city, district, price, area, lang=lang)
            except Exception as _e:
                st.error(f"Neighborhood error: {_e}")

        # ---------- TAB 9: MORTGAGE CALCULATOR ----------
        with tab9:
            try:
                render_mortgage_calculator(price, lang=lang)
            except Exception as _e:
                st.error(f"Mortgage error: {_e}")

else:
    empty_html = (
        '<div class="empty-box">'
        '<div class="empty-icon">🏠</div>'
        '<div class="empty-title">' + L['empty_title'] + '</div>'
        '<div class="empty-text">' + L['empty_text'] + ' <b>' + L['empty_text2'] + '</b></div>'
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
    '<div class="market-item"><div class="market-label">' + L["market_avg"] + '</div><div class="market-value">' + f'{avg_ppm:,.0f}' + (' جنيه/م²' if lang == 'ar' else ' EGP/m2') + '</div></div>'
    '<div class="market-item"><div class="market-label">' + L["top_city"] + '</div><div class="market-value">' + (CITY_NAMES.get(top_cities[0][0], top_cities[0][0]) if lang == 'ar' else top_cities[0][0]) + '</div></div>'
    '<div class="market-item"><div class="market-label">' + L["data_source"] + '</div><div class="market-value">PropertyFinder</div></div>'
    '</div>'
)
st.markdown(market_html, unsafe_allow_html=True)


# ============================================================
# FAQ CARDS
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## ❓ " + L["faq_title"])

faq_items = [
    (L['faq_q1'], L['faq_a1']),
    (L['faq_q2'], L['faq_a2']),
    (L['faq_q3'], L['faq_a3']),
    (L['faq_q4'], L['faq_a4']),
    (L['faq_q5'], L['faq_a5']),
    (L['faq_q6'], L['faq_a6']),
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
    '<h3 style="font-size:1.3rem;font-weight:900;margin:0 0 0.5rem 0;">' + L['agent_title'] + '</h3>'
    '<p style="opacity:0.95;font-size:0.88rem;margin:0 0 1.25rem 0;">' + L['agent_text'] + '</p>'
    '<div style="display:flex;justify-content:center;gap:0.5rem;flex-wrap:wrap;">'
    '<a href="https://www.propertyfinder.eg" target="_blank" style="background:white;color:#6366f1;padding:0.7rem 1.25rem;border-radius:100px;font-weight:800;text-decoration:none;font-size:0.85rem;">' + L['agent_browse'] + '</a>'
    '<a href="https://wa.me/?text=Hi%2C%20I%20need%20a%20property%20valuation" target="_blank" style="background:rgba(255,255,255,0.2);color:white;padding:0.7rem 1.25rem;border-radius:100px;font-weight:800;text-decoration:none;font-size:0.85rem;border:1px solid rgba(255,255,255,0.3);">' + L['agent_contact'] + '</a>'
    '</div></div>'
)
st.markdown(agent_html, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
footer_html = (
    '<div class="footer-box">'
    '<b>Smart House Price Predictor</b> v11.0 · '
    + metadata['model_name'] + ' · '
    + f"R² {m['r2']:.4f}" + ' · '
    + f"MAPE {m['mape']:.2f}%" + '<br>'
    + L['footer_trained']
    + '<br><br>'
    + L['footer_disclaimer']
    + '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
