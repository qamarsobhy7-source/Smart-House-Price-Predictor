"""Saved searches — like Property Finder / Bayut."""
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
SAVES_FILE = DATA / "saved_searches.json"


def _load_all():
    if SAVES_FILE.exists():
        try:
            return json.loads(SAVES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_all(items):
    SAVES_FILE.parent.mkdir(exist_ok=True)
    SAVES_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_search(data, lang="en"):
    """Save a search. data = dict of filters."""
    items = _load_all()
    item = {
        "id": f"search_{len(items) + 1}_{int(datetime.now().timestamp())}",
        "saved_at": datetime.now().isoformat(),
        **data,
    }
    items.append(item)
    _save_all(items)
    return item["id"]


def delete_search(search_id):
    items = _load_all()
    items = [x for x in items if x.get("id") != search_id]
    _save_all(items)


def get_saved_searches():
    return _load_all()


def _format_search(item, lang="en"):
    """Human-readable summary."""
    parts = []
    if item.get("governorate"):
        parts.append(item["governorate"])
    if item.get("district"):
        parts.append(item["district"])
    if item.get("bedrooms"):
        parts.append(f"{item['bedrooms']} غرف" if lang == "ar" else f"{item['bedrooms']} BD")
    if item.get("price_range"):
        parts.append(item["price_range"])
    return " · ".join(parts) if parts else "—"


def render_save_search_button(filters, lang="en"):
    """Render Save Search button."""
    label = "💾 حفظ البحث" if lang == "ar" else "💾 Save Search"
    saved_label = "✅ تم الحفظ" if lang == "ar" else "✅ Saved"
    if st.button(label, key="save_search_btn"):
        save_search(filters, lang)
        st.toast(saved_label, icon="🔎")
        st.rerun()


def render_saved_searches(lang="en"):
    """Render saved searches list (sidebar)."""
    items = get_saved_searches()
    if not items:
        return

    title = "🔎 البحثات المحفوظة" if lang == "ar" else "🔎 Saved Searches"
    with st.expander(f"{title} ({len(items)})", expanded=False):
        for item in reversed(items[-10:]):
            col1, col2 = st.columns([4, 1])
            with col1:
                summary = _format_search(item, lang)
                st.markdown(f"**{summary}**")
                st.caption(f"📅 {item.get('saved_at', '')[:10]}")
            with col2:
                if st.button("🗑️", key=f"del_search_{item.get('id', '')}"):
                    delete_search(item.get("id"))
                    st.rerun()
            st.markdown("---")
