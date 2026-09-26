"""Featured properties — with Sort + Count controls."""
import json
import pandas as pd
import streamlit as st
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


@st.cache_data
def _load_listings():
    f = DATA / "real_data" / "model_ready_clean.csv"
    if f.exists():
        return pd.read_csv(f)
    return pd.DataFrame()


@st.cache_data
def _load_translations():
    f = DATA / "place_translations.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {}


def _t(key, lang):
    m = _load_translations()
    return m.get(key, key) if lang == "ar" else key


def get_featured(seed=42, n=4, sort_by="featured"):
    """Return N featured properties — one from each district (no duplicates)."""
    df = _load_listings()
    if df.empty:
        return []

    # Top districts
    top = ["New Cairo City", "Sheikh Zayed City", "6 October City", "Hurghada",
           "Mostakbal City - Future City", "Madinaty", "Al Alamein", "New Capital City",
           "Hay Sharq", "Al Ain Al Sokhna"]

    # عقار واحد من كل حي (بدون تكرار)
    rows = []
    for d in top:
        sub = df[df["district"] == d]
        if len(sub) > 0:
            # نختار عقار متوسط السعر
            median_price = sub["price"].median()
            sample = sub.iloc[(sub["price"] - median_price).abs().argsort()[:1]]
            if len(sample) > 0:
                rows.append(sample.iloc[0].to_dict())

    # نحول لـ DataFrame
    result = pd.DataFrame(rows)
    if result.empty:
        return []

    # الترتيب
    if sort_by == "price_asc":
        result = result.sort_values("price", ascending=True)
    elif sort_by == "price_desc":
        result = result.sort_values("price", ascending=False)
    elif sort_by == "size_desc":
        result = result.sort_values("size", ascending=False)
    elif sort_by == "size_asc":
        result = result.sort_values("size", ascending=True)

    return result.head(n).to_dict("records")


def _fmt_price(p):
    if p >= 1_000_000:
        return f"{p/1_000_000:.2f}M"
    return f"{p/1_000:.0f}K"


def _card(p, lang):
    """Compact property card."""
    district = _t(str(p.get("district", "")), lang)
    city = _t(str(p.get("city", "")), lang)
    price = p.get("price", 0)
    size = p.get("size", 0)
    beds = p.get("bedrooms", 0)
    baths = p.get("bathrooms", 0)

    bd_lbl = "غرف" if lang == "ar" else "BD"
    ba_lbl = "حمام" if lang == "ar" else "BA"
    egp_lbl = "جنيه" if lang == "ar" else "EGP"
    m2 = "م²"

    return (
        '<div style="background:white;border:1px solid #e5e7eb;'
        'border-radius:16px;overflow:hidden;'
        'box-shadow:0 4px 16px rgba(0,0,0,0.06);'
        'transition:all 0.2s;height:100%;">'
        '<div style="height:110px;'
        'background:linear-gradient(135deg,#667eea,#764ba2);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:44px;position:relative;">🏢'
        '<div style="position:absolute;top:8px;right:8px;'
        'background:linear-gradient(135deg,#f093fb,#f5576c);color:white;'
        'padding:3px 8px;border-radius:100px;font-size:9px;font-weight:800;'
        'letter-spacing:0.4px;">★ '
        + ('مميز' if lang == 'ar' else 'FEATURED') + '</div></div>'
        '<div style="padding:12px;">'
        '<div style="font-size:13px;font-weight:800;color:#1f2937;'
        'margin-bottom:3px;overflow:hidden;text-overflow:ellipsis;'
        'white-space:nowrap;">' + district + '</div>'
        '<div style="font-size:10px;color:#6b7280;margin-bottom:10px;">'
        '📍 ' + city + '</div>'
        '<div style="display:flex;gap:6px;margin-bottom:10px;font-size:10px;">'
        '<div style="flex:1;background:#f3f4f6;border-radius:6px;'
        'padding:4px 2px;text-align:center;font-weight:700;color:#374151;">'
        + str(int(size)) + ' ' + m2 + '</div>'
        '<div style="flex:1;background:#f3f4f6;border-radius:6px;'
        'padding:4px 2px;text-align:center;font-weight:700;color:#374151;">'
        + str(int(beds)) + ' ' + bd_lbl + '</div>'
        '<div style="flex:1;background:#f3f4f6;border-radius:6px;'
        'padding:4px 2px;text-align:center;font-weight:700;color:#374151;">'
        + str(int(baths)) + ' ' + ba_lbl + '</div>'
        '</div>'
        '<div style="border-top:1px solid #f3f4f6;padding-top:8px;'
        'display:flex;justify-content:space-between;align-items:baseline;">'
        '<div style="font-size:16px;font-weight:900;color:#10b981;">'
        + _fmt_price(price) + '</div>'
        '<div style="font-size:9px;color:#9ca3af;font-weight:700;">'
        + egp_lbl + '</div>'
        '</div></div></div>'
    )


def render_featured_properties(lang="en"):
    """Render featured properties — with sort + count controls."""
    title = "⭐ عقارات مميزة" if lang == "ar" else "⭐ Featured Properties"
    sub = ("مختارة من أفضل المناطق" if lang == "ar"
           else "Selected from top districts")

    # Sort + Count
    sort_opts_en = {
        "featured": "✨ Featured first",
        "price_asc": "💰 Price: Low to High",
        "price_desc": "💰 Price: High to Low",
        "size_desc": "📐 Size: Large first",
        "size_asc": "📐 Size: Small first",
    }
    sort_opts_ar = {
        "featured": "✨ مميزة أولاً",
        "price_asc": "💰 السعر: من الأقل",
        "price_desc": "💰 السعر: من الأعلى",
        "size_desc": "📐 المساحة: الأكبر",
        "size_asc": "📐 المساحة: الأصغر",
    }
    sort_opts = sort_opts_ar if lang == "ar" else sort_opts_en

    count_opts = {
        "4": "4",
        "8": "8",
        "12": "12",
    }

    # Header + Controls
    hc1, hc2, hc3 = st.columns([4, 1.3, 0.8])
    with hc1:
        header = (
            '<div style="display:flex;align-items:center;gap:10px;">'
            '<div style="font-size:24px;">⭐</div>'
            '<div>'
            '<div style="font-size:18px;font-weight:900;color:#1f2937;">'
            + title + '</div>'
            '<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
            + sub + '</div>'
            '</div></div>'
        )
        st.markdown(header, unsafe_allow_html=True)

    with hc2:
        sort_label = "🔀 ترتيب" if lang == "ar" else "🔀 Sort by"
        sort_key = st.selectbox(
            sort_label,
            options=list(sort_opts.keys()),
            format_func=lambda x: sort_opts[x],
            key="feat_sort",
        )

    with hc3:
        count_label = "👁️ عدد" if lang == "ar" else "👁️ Show"
        count_n = st.selectbox(
            count_label,
            options=list(count_opts.keys()),
            index=0,
            key="feat_count",
        )

    # Get properties
    props = get_featured(n=int(count_n), sort_by=sort_key)
    if not props:
        return

    # Render grid (4 columns)
    cols = st.columns(4)
    for i, prop in enumerate(props):
        with cols[i % 4]:
            st.markdown(_card(prop, lang), unsafe_allow_html=True)
