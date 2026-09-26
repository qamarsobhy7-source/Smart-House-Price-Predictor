"""Nearby transport module."""
import json
import streamlit as st
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


# خريطة ترجمة الخطوط
METRO_LINES_EN = {
    "الخط الأول": "Line 1",
    "الخط الثاني": "Line 2",
    "الخط الثالث": "Line 3",
    "الخط الثالث (قادم)": "Line 3 (upcoming)",
    "الخط الرابع": "Line 4",
    "الخط الرابع (قادم)": "Line 4 (upcoming)",
}


@st.cache_data
def _load_trans():
    f = DATA / "nearby_transport.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {}


def get_transport(district):
    """Return nearby metro/bus/airport info."""
    data = _load_trans()
    return data.get(district, {
        "metro": [], "bus": 0, "airport_km": None, "train": False,
    })


def _metro_label(line, lang):
    """Translate metro line based on language."""
    if lang == "en":
        return METRO_LINES_EN.get(line, line)
    return line


def render_transport(district, lang="en"):
    """Render transport info."""
    info = get_transport(district)

    title = "🚇 المواصلات القريبة" if lang == "ar" else "🚇 Nearby Transport"
    metro_lbl = "خط المترو" if lang == "ar" else "Metro Line"
    bus_lbl = "محطات باص" if lang == "ar" else "Bus Stations"
    air_lbl = "المطار (كم)" if lang == "ar" else "Airport (km)"
    train_lbl = "محطة قطار" if lang == "ar" else "Train Station"
    yes_lbl = "متاح" if lang == "ar" else "Available"
    no_lbl = "غير متاح" if lang == "ar" else "Not available"

    st.markdown("#### " + title)

    metro = info.get("metro", [])
    metro_translated = [_metro_label(m, lang) for m in metro]
    metro_str = ", ".join(metro_translated) if metro_translated else ("لا يوجد" if lang == "ar" else "None")
    bus_count = info.get("bus", 0)
    airport = info.get("airport_km", "—")
    train = yes_lbl if info.get("train", False) else no_lbl

    cols = st.columns(4)
    items = [
        ("🚇", metro_lbl, metro_str),
        ("🚌", bus_lbl, str(bus_count)),
        ("✈️", air_lbl, str(airport)),
        ("🚂", train_lbl, train),
    ]
    for col, (icon, lbl, val) in zip(cols, items):
        with col:
            html = (
                '<div style="background:white;border:1px solid #e5e7eb;'
                'border-radius:12px;padding:14px 8px;text-align:center;">'
                '<div style="font-size:24px;margin-bottom:4px;">' + icon + '</div>'
                '<div style="font-size:13px;font-weight:900;color:#6366f1;">'
                + val + '</div>'
                '<div style="font-size:10px;color:#6b7280;font-weight:600;'
                'margin-top:4px;text-transform:uppercase;">' + lbl + '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
