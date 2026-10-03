"""Save/Favorite properties — session-based."""
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
SAVES_FILE = DATA / "saved_properties.json"


def _load_saves():
    """Load all saved properties."""
    if SAVES_FILE.exists():
        try:
            return json.loads(SAVES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _to_native(obj):
    """Convert numpy types to native Python for JSON."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(x) for x in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _save_all(items):
    SAVES_FILE.parent.mkdir(exist_ok=True)
    items = _to_native(items)
    SAVES_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def save_property(data, lang="en"):
    """Save a property. data = dict with property info."""
    items = _load_saves()
    item = {
        "id": f"prop_{len(items) + 1}_{int(datetime.now().timestamp())}",
        "saved_at": datetime.now().isoformat(),
        **data,
    }
    items.append(item)
    _save_all(items)
    return item["id"]


def delete_saved(prop_id):
    items = _load_saves()
    items = [x for x in items if x.get("id") != prop_id]
    _save_all(items)


def get_saved():
    return _load_saves()


def render_save_button(property_data, lang="en"):
    """Render save/favorite button."""
    label = "💾 حفظ العقار" if lang == "ar" else "💾 Save Property"
    saved_label = "✅ تم الحفظ" if lang == "ar" else "✅ Saved"

    if st.button(label, key="save_property_btn"):
        try:
            save_property(property_data, lang)
            st.toast(saved_label, icon="💾")
            st.rerun()
        except Exception as e:
            st.error(f"❌ {e}")


def render_saved_list(lang="en"):
    """Render saved properties list in sidebar or expander."""
    items = get_saved()
    if not items:
        return

    title = "💾 العقارات المحفوظة" if lang == "ar" else "💾 Saved Properties"
    with st.expander(f"{title} ({len(items)})", expanded=False):
        for item in reversed(items[-10:]):
            col1, col2 = st.columns([4, 1])
            with col1:
                area = item.get("area", "?")
                district = item.get("district", "?")
                price = item.get("price", 0)
                st.markdown(
                    f"**{area}m²** — {district}  \n"
                    f"💰 **{price:,.0f} EGP**"
                )
                st.caption(f"📅 {item.get('saved_at', '')[:10]}")
            with col2:
                if st.button("🗑️", key=f"del_{item.get('id', '')}"):
                    delete_saved(item.get("id"))
                    st.rerun()
            st.markdown("---")
