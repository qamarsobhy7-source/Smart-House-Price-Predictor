"""
Hierarchical location selector v2 — matches Property Finder / Bayut UX.
"""
import json
from pathlib import Path
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


@st.cache_data
def _load_hierarchy():
    return json.loads((DATA / "egypt_hierarchy.json").read_text(encoding="utf-8"))


@st.cache_data
def _load_translations():
    return json.loads((DATA / "place_translations.json").read_text(encoding="utf-8"))


STATUS_ICONS = {
    "high": "🟢", "medium": "🟡", "low": "🟠",
    "minimal": "🔴", "coming_soon": "⚪",
}
STATUS_LABELS = {
    "ar": {
        "high": "بيانات كاملة", "medium": "بيانات جيدة",
        "low": "بيانات محدودة", "minimal": "بيانات ضعيفة",
        "coming_soon": "قريباً",
    },
    "en": {
        "high": "Full data", "medium": "Good data",
        "low": "Limited data", "minimal": "Sparse data",
        "coming_soon": "Coming soon",
    },
}


def _t(key, lang):
    mapping = _load_translations()
    return mapping.get(key, key) if lang == "ar" else key


def _step_header(num, title, subtitle, lang):
    """Render a numbered step header like Property Finder."""
    return (
        f'<div style="display:flex;align-items:center;gap:12px;'
        f'margin:18px 0 8px 0;">'
        f'<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);'
        f'color:white;width:32px;height:32px;border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-weight:800;font-size:14px;flex-shrink:0;">{num}</div>'
        f'<div>'
        f'<div style="font-weight:700;font-size:15px;color:#1f2937;">{title}</div>'
        f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">{subtitle}</div>'
        f'</div></div>'
    )


def _breadcrumb(items, lang):
    """Show selection breadcrumb like Bayut."""
    if not items:
        return ""
    parts = []
    for i, (icon, label) in enumerate(items):
        if i > 0:
            parts.append('<span style="color:#9ca3af;margin:0 6px;">›</span>')
        parts.append(
            f'<span style="color:#6366f1;font-weight:600;font-size:13px;">'
            f'{icon} {label}</span>'
        )
    return (
        '<div style="background:#f9fafb;border:1px solid #e5e7eb;'
        'border-radius:10px;padding:10px 14px;margin:10px 0 20px 0;">'
        + "".join(parts) + '</div>'
    )


def render_hierarchical_selector(lang="en"):
    """Enhanced 5-level cascading selector."""
    hier = _load_hierarchy()
    govs = hier["governorates"]

    # ── Labels ──
    labels = {
        "ar": {
            "gov_title": "المحافظة", "gov_sub": "اختار المحافظة اللي فيها العقار",
            "city_title": "المدينة", "city_sub": "المدينة داخل المحافظة",
            "dist_title": "الحي", "dist_sub": "الحي أو المنطقة داخل المدينة",
            "comp_title": "الكومبوند / المشروع", "comp_sub": "اختياري — تخطاه لو مش معروف",
            "all": "— الكل —", "none": "— لا يوجد —",
            "listings": "عقار", "soon": "قريباً",
            "no_data": "مفيش بيانات", "warning": "البيانات محدودة — التوقعات تقريبية",
        },
        "en": {
            "gov_title": "Governorate", "gov_sub": "Choose the governorate",
            "city_title": "City", "city_sub": "City within the governorate",
            "dist_title": "District", "dist_sub": "District or area within the city",
            "comp_title": "Compound / Project", "comp_sub": "Optional — skip if unknown",
            "all": "— All —", "none": "— None —",
            "listings": "listings", "soon": "Coming soon",
            "no_data": "No data", "warning": "Limited data — estimates are approximate",
        },
    }[lang]

    # ═══════════════════════════════════════════════
    # 1) GOVERNORATE
    # ═══════════════════════════════════════════════
    st.markdown(
        _step_header(1, labels["gov_title"], labels["gov_sub"], lang),
        unsafe_allow_html=True,
    )

    gov_items = []
    for g in govs:
        label = g["ar"] if lang == "ar" else g["en"]
        icon = STATUS_ICONS[g["data_status"]]
        count = g["listings"]
        if count > 0:
            disp = f"{icon} {label}  ({count:,} {labels['listings']})"
        else:
            disp = f"{icon} {label}  — {labels['soon']}"
        gov_items.append({
            "en": g["en"], "ar": g["ar"], "code": g["code"],
            "status": g["data_status"], "count": count,
            "display": disp, "data": g,
        })

    gov_choice = st.selectbox(
        " ",
        options=range(len(gov_items)),
        format_func=lambda i: gov_items[i]["display"],
        key="h_gov_v2",
        label_visibility="collapsed",
    )
    sel_gov = gov_items[gov_choice]
    gov_data = sel_gov["data"]

    if gov_data["data_status"] == "coming_soon":
        st.warning(
            "🚧 المحافظة دي قريباً — نعمل على إضافة بياناتها."
            if lang == "ar"
            else "🚧 This governorate is coming soon."
        )
        return None

    # ═══════════════════════════════════════════════
    # 2) CITY
    # ═══════════════════════════════════════════════
    st.markdown(
        _step_header(2, labels["city_title"], labels["city_sub"], lang),
        unsafe_allow_html=True,
    )

    real_cities = sorted({c["source_city"] for c in gov_data["cities_with_data"]})

    # لو فيه مدينة واحدة بس — نختارها تلقائياً (نفس Property Finder)
    if len(real_cities) == 1:
        sel_city = real_cities[0]
        city_label = _t(sel_city, lang)
        total = sum(x["listings"] for x in gov_data["cities_with_data"])
        st.info(
            f"📍 {city_label} — {total:,} {labels['listings']}  ✓"
            if lang == "ar"
            else f"📍 {city_label} — {total:,} {labels['listings']}  ✓"
        )
    else:
        city_items = [{"name": "all", "display": labels["all"]}]
        for c in real_cities:
            cnt = sum(x["listings"] for x in gov_data["cities_with_data"] if x["source_city"] == c)
            city_items.append({
                "name": c,
                "display": f"{_t(c, lang)}  ({cnt:,} {labels['listings']})",
            })

        city_choice = st.selectbox(
            " ",
            options=range(len(city_items)),
            format_func=lambda i: city_items[i]["display"],
            key="h_city_v2",
            label_visibility="collapsed",
        )
        sel_city = city_items[city_choice]["name"]

    # ═══════════════════════════════════════════════
    # 3) DISTRICT
    # ═══════════════════════════════════════════════
    st.markdown(
        _step_header(3, labels["dist_title"], labels["dist_sub"], lang),
        unsafe_allow_html=True,
    )

    districts = gov_data["cities_with_data"]
    if sel_city != "all":
        districts = [d for d in districts if d["source_city"] == sel_city]

    dist_items = [{"name": "all", "display": labels["all"]}]
    for d in districts:
        dist_items.append({
            "name": d["en"],
            "display": f"{_t(d['en'], lang)}  ({d['listings']:,} {labels['listings']})",
        })

    dist_choice = st.selectbox(
        " ",
        options=range(len(dist_items)),
        format_func=lambda i: dist_items[i]["display"],
        key="h_dist_v2",
        label_visibility="collapsed",
    )
    sel_dist = dist_items[dist_choice]["name"]

    # ═══════════════════════════════════════════════
    # 4) COMPOUND
    # ═══════════════════════════════════════════════
    st.markdown(
        _step_header(4, labels["comp_title"], labels["comp_sub"], lang),
        unsafe_allow_html=True,
    )

    compounds = []
    if sel_dist != "all":
        for d in districts:
            if d["en"] == sel_dist:
                compounds = d.get("compounds", [])
                break
    else:
        for d in districts:
            compounds.extend(d.get("compounds", []))
        compounds = sorted(set(compounds))

    comp_items = [{"name": "None", "display": labels["none"]}]
    for c in compounds:
        comp_items.append({
            "name": c,
            "display": _t(c, lang),
        })

    comp_choice = st.selectbox(
        " ",
        options=range(len(comp_items)),
        format_func=lambda i: comp_items[i]["display"],
        key="h_comp_v2",
        label_visibility="collapsed",
    )
    sel_comp = comp_items[comp_choice]["name"]

    # ═══════════════════════════════════════════════
    # 5) BREADCRUMB (زي Bayut)
    # ═══════════════════════════════════════════════
    crumbs = [("🏛️", _t(sel_gov["en"], lang))]
    if sel_city != "all":
        crumbs.append(("🏙️", _t(sel_city, lang)))
    if sel_dist != "all":
        crumbs.append(("🏘️", _t(sel_dist, lang)))
    if sel_comp not in ("None", "all"):
        crumbs.append(("🏢", _t(sel_comp, lang)))

    st.markdown(_breadcrumb(crumbs, lang), unsafe_allow_html=True)

    # ═══════════════════════════════════════════════
    # 6) WARNING لو بيانات محدودة
    # ═══════════════════════════════════════════════
    if sel_gov["status"] in ("low", "minimal"):
        st.warning(f"⚠️ {labels['warning']}")

    # ═══════════════════════════════════════════════
    # 7) RETURN
    # ═══════════════════════════════════════════════
    # لو "all" — نختار أول قيمة حقيقية
    final_city = sel_city
    final_dist = sel_dist
    if final_city == "all":
        real = sorted({c["source_city"] for c in gov_data["cities_with_data"]})
        final_city = real[0] if real else "Cairo"
    if final_dist == "all":
        real = [c for c in gov_data["cities_with_data"] if c["source_city"] == final_city]
        final_dist = real[0]["en"] if real else "New Cairo City"

    return {
        "governorate_en": sel_gov["en"],
        "governorate_ar": sel_gov["ar"],
        "governorate_code": sel_gov["code"],
        "city": final_city,
        "district": final_dist,
        "compound": sel_comp,
        "data_status": sel_gov["status"],
    }
