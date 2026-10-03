"""Safety & School ratings module."""
import json
import streamlit as st
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


@st.cache_data
def _load_safety():
    f = DATA / "safety_schools.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {}


def get_safety(district):
    data = _load_safety()
    return data.get(district, {
        "safety": 70, "schools_rating": 65,
        "schools_intl": 0, "schools_public": 0,
    })


def _rating_color(v):
    if v >= 80: return "#10b981"
    if v >= 65: return "#84cc16"
    if v >= 50: return "#f59e0b"
    return "#ef4444"


def render_safety_schools(district, lang="en"):
    info = get_safety(district)

    title = "🛡️ الأمان والتعليم" if lang == "ar" else "🛡️ Safety & Education"

    safety_lbl = "درجة الأمان" if lang == "ar" else "Safety Score"
    schools_lbl = "تقييم المدارس" if lang == "ar" else "Schools Rating"
    intl_lbl = "مدارس دولية" if lang == "ar" else "Intl Schools"
    pub_lbl = "مدارس حكومية" if lang == "ar" else "Public Schools"

    st.markdown("#### " + title)

    sc = info.get("safety", 70)
    sr = info.get("schools_rating", 65)
    intl = info.get("schools_intl", 0)
    pub = info.get("schools_public", 0)

    cols = st.columns(4)
    items = [
        ("🛡️", safety_lbl, str(sc), _rating_color(sc)),
        ("🏫", schools_lbl, str(sr), _rating_color(sr)),
        ("🌍", intl_lbl, str(intl), "#6366f1"),
        ("🏛️", pub_lbl, str(pub), "#6366f1"),
    ]

    for col, (icon, lbl, val, color) in zip(cols, items):
        with col:
            html = (
                '<div style="background:white;border:2px solid ' + color + ';'
                'border-radius:12px;padding:14px 8px;text-align:center;">'
                '<div style="font-size:24px;margin-bottom:4px;">' + icon + '</div>'
                '<div style="font-size:20px;font-weight:900;color:' + color + ';">'
                + val + '</div>'
                '<div style="font-size:10px;color:#6b7280;font-weight:700;'
                'margin-top:4px;text-transform:uppercase;">' + lbl + '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
