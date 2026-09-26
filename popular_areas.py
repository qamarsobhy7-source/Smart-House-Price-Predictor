"""
Popular areas module — matches Property Finder / Bayut.
"""
import json
import pandas as pd
import streamlit as st
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


@st.cache_data
def _load_map_data():
    """Load full listings data (7,749 records)."""
    f = DATA / "real_data" / "model_ready_clean.csv"
    if f.exists():
        df = pd.read_csv(f)
        # نضيف عمود price_m للسعر بالمليون
        if 'price' in df.columns and 'price_m' not in df.columns:
            df['price_m'] = df['price'] / 1e6
        return df
    # fallback للعينة
    f2 = DATA / "real_data" / "map_data.csv"
    if f2.exists():
        return pd.read_csv(f2)
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


def get_popular_areas(top_n=8):
    df = _load_map_data()
    if df.empty:
        return []
    areas = []
    for district in df["district"].dropna().unique():
        sub = df[df["district"] == district]
        if len(sub) < 5:
            continue
        areas.append({
            "district": district,
            "city": sub["city"].iloc[0] if "city" in sub.columns else "Cairo",
            "listings": len(sub),
            "avg_price_m": sub["price_m"].mean() if "price_m" in sub.columns else 0,
            "avg_size": sub["size"].mean() if "size" in sub.columns else 0,
        })
    areas.sort(key=lambda x: -x["listings"])
    return areas[:top_n]


def _card_html(district_ar, city_ar, price_m, listings, lbl_per_m, lbl_listings):
    return (
        '<div style="background:white;border:1px solid #e5e7eb;'
        'border-radius:16px;padding:16px;margin-bottom:12px;'
        'box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
        '<div style="font-size:14px;font-weight:800;color:#1f2937;'
        'margin-bottom:6px;">🏘️ ' + district_ar + '</div>'
        '<div style="font-size:11px;color:#6b7280;margin-bottom:10px;">'
        '📍 ' + city_ar + '</div>'
        '<div style="display:flex;justify-content:space-between;'
        'align-items:end;border-top:1px solid #f3f4f6;padding-top:10px;">'
        '<div>'
        '<div style="font-size:17px;font-weight:900;color:#10b981;">'
        + str(round(price_m, 1)) + '</div>'
        '<div style="font-size:9px;color:#9ca3af;text-transform:uppercase;'
        'font-weight:700;">' + lbl_per_m + '</div>'
        '</div>'
        '<div style="text-align:right;">'
        '<div style="font-size:14px;font-weight:800;color:#6366f1;">'
        + str(listings) + '</div>'
        '<div style="font-size:9px;color:#9ca3af;text-transform:uppercase;'
        'font-weight:700;">' + lbl_listings + '</div>'
        '</div>'
        '</div>'
        '</div>'
    )


def render_popular_areas(lang="en"):
    areas = get_popular_areas(8)
    if not areas:
        return

    title = "🔥 المناطق الأكثر طلباً" if lang == "ar" else "🔥 Popular Areas"
    subtitle = (
        "أشهر المناطق بأكبر عدد من العقارات" if lang == "ar"
        else "Top neighborhoods with most listings"
    )

    header = (
        '<div style="margin:32px 0 16px 0;">'
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">'
        '<div style="font-size:28px;">🔥</div>'
        '<div>'
        '<div style="font-size:22px;font-weight:900;color:#1f2937;">'
        + title + '</div>'
        '<div style="font-size:12px;color:#6b7280;margin-top:2px;">'
        + subtitle + '</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(header, unsafe_allow_html=True)

    lbl_listings = "عقار" if lang == "ar" else "listings"
    lbl_per_m = "M EGP" if lang == "ar" else "M EGP"

    cols = st.columns(4)
    for i, area in enumerate(areas):
        col = cols[i % 4]
        with col:
            html = _card_html(
                _t(area["district"], lang),
                _t(area["city"], lang),
                area["avg_price_m"],
                area["listings"],
                lbl_per_m,
                lbl_listings,
            )
            st.markdown(html, unsafe_allow_html=True)
