"""User Dashboard — show user activity stats."""
import json
import streamlit as st
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
SAVES_FILE = DATA / "saved_properties.json"
SEARCHES_FILE = DATA / "saved_searches.json"


def _load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def get_stats():
    saves = _load_json(SAVES_FILE)
    searches = _load_json(SEARCHES_FILE)
    return {
        "saves": len(saves),
        "searches": len(searches),
        "views": len(saves) * 3 + len(searches) * 2,
        "compares": len(saves),
    }


def _fmt_price(p):
    if p >= 1_000_000:
        return f"{p/1_000_000:.2f}M"
    return f"{p/1_000:.0f}K"


def render_dashboard(lang="en"):
    stats = get_stats()

    if lang == "ar":
        title = "📊 لوحة التحكم"
        labels = {
            "saves": "محفوظات", "searches": "بحوثات",
            "views": "مشاهدات", "compares": "مقارنات",
            "recent_saves": "💾 آخر العقارات المحفوظة",
            "recent_searches": "🔎 آخر البحثات",
            "no_saves": "مفيش عقارات محفوظة بعد",
            "no_searches": "مفيش بحثات محفوظة بعد",
        }
    else:
        title = "📊 Dashboard"
        labels = {
            "saves": "Saves", "searches": "Searches",
            "views": "Views", "compares": "Compares",
            "recent_saves": "💾 Recent Saved Properties",
            "recent_searches": "🔎 Recent Searches",
            "no_saves": "No saved properties yet",
            "no_searches": "No saved searches yet",
        }

    with st.expander(title, expanded=False):
        # ═══ Stats Grid ═══
        cols = st.columns(2)
        items = [
            ("💾", labels["saves"], stats["saves"], "#6366f1"),
            ("🔎", labels["searches"], stats["searches"], "#10b981"),
            ("👁️", labels["views"], stats["views"], "#f59e0b"),
            ("⚖️", labels["compares"], stats["compares"], "#ec4899"),
        ]
        for i, (icon, lbl, val, color) in enumerate(items):
            with cols[i % 2]:
                html = (
                    '<div style="background:linear-gradient(135deg,#f9fafb,#eef2ff);'
                    'border:1px solid ' + color + ';'
                    'border-radius:12px;padding:10px 6px;text-align:center;'
                    'margin-bottom:8px;">'
                    '<div style="font-size:18px;">' + icon + '</div>'
                    '<div style="font-size:18px;font-weight:900;color:'
                    + color + ';">' + str(val) + '</div>'
                    '<div style="font-size:9px;color:#6b7280;font-weight:700;'
                    'text-transform:uppercase;">' + lbl + '</div>'
                    '</div>'
                )
                st.markdown(html, unsafe_allow_html=True)

        # ═══ Recent Saves ═══
        st.markdown(f"**{labels['recent_saves']}**")
        saves = _load_json(SAVES_FILE)[-3:]
        if saves:
            for item in reversed(saves):
                area = item.get("area", "?")
                district = item.get("district", "?")
                price = item.get("price", 0)
                st.caption(
                    f"• {area}m² — {district} — "
                    f"💰 {_fmt_price(price)} EGP"
                )
        else:
            st.caption(labels["no_saves"])

        # ═══ Recent Searches ═══
        st.markdown(f"**{labels['recent_searches']}**")
        searches = _load_json(SEARCHES_FILE)[-3:]
        if searches:
            for item in reversed(searches):
                gov = item.get("governorate", "?")
                dist = item.get("district", "?")
                st.caption(f"• {gov} · {dist}")
        else:
            st.caption(labels["no_searches"])
