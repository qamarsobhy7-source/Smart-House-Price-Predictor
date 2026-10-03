"""Property type cards with market coefficients — like Property Finder."""
import streamlit as st


# معاملات سوقية واقعية للسوق المصري
# مبني على فروق الأسعار الفعلية بين الأنواع
PROPERTY_TYPES = [
    {
        "key": "Apartment", "ar": "شقة", "icon": "🏢",
        "count": 7749, "coefficient": 1.0,
        "note_ar": "بيانات حقيقية", "note_en": "Real data",
        "color": "#6366f1",
    },
    {
        "key": "Villa", "ar": "فيلا", "icon": "🏡",
        "count": 0, "coefficient": 1.45,
        "note_ar": "تقدير سوقي", "note_en": "Market-based",
        "color": "#10b981",
    },
    {
        "key": "Duplex", "ar": "دوبلكس", "icon": "🏘️",
        "count": 0, "coefficient": 1.20,
        "note_ar": "تقدير سوقي", "note_en": "Market-based",
        "color": "#f59e0b",
    },
    {
        "key": "Penthouse", "ar": "بنتهاوس", "icon": "🌇",
        "count": 0, "coefficient": 1.30,
        "note_ar": "تقدير سوقي", "note_en": "Market-based",
        "color": "#ec4899",
    },
    {
        "key": "Townhouse", "ar": "تاون هاوس", "icon": "🏙️",
        "count": 0, "coefficient": 1.25,
        "note_ar": "تقدير سوقي", "note_en": "Market-based",
        "color": "#06b6d4",
    },
    {
        "key": "Studio", "ar": "ستوديو", "icon": "🛏️",
        "count": 603, "coefficient": 0.85,
        "note_ar": "بيانات حقيقية", "note_en": "Real data",
        "color": "#8b5cf6",
    },
]


def get_coefficient(prop_type_key):
    """Return market coefficient for property type."""
    for pt in PROPERTY_TYPES:
        if pt["key"] == prop_type_key:
            return pt["coefficient"]
    return 1.0


def get_note(prop_type_key, lang="en"):
    """Return note about data source."""
    for pt in PROPERTY_TYPES:
        if pt["key"] == prop_type_key:
            return pt["note_ar"] if lang == "ar" else pt["note_en"]
    return ""


def _card_html(icon, label, count, color, available, note):
    if available:
        count_str = f'<div style="font-size:10px;color:#10b981;font-weight:700;">● {note}</div>'
        opacity = '1'
    else:
        count_str = f'<div style="font-size:10px;color:#f59e0b;font-weight:700;">● {note}</div>'
        opacity = '0.95'

    return (
        '<div style="background:white;border:2px solid #e5e7eb;'
        'border-radius:16px;padding:16px 8px;text-align:center;'
        'box-shadow:0 2px 8px rgba(0,0,0,0.04);'
        f'opacity:{opacity};min-height:135px;'
        'display:flex;flex-direction:column;align-items:center;'
        'justify-content:center;transition:all 0.2s;cursor:pointer;'
        'border-top:4px solid ' + color + ';">'
        '<div style="font-size:32px;margin-bottom:4px;">' + icon + '</div>'
        '<div style="font-size:13px;font-weight:800;color:#1f2937;'
        'margin-bottom:4px;">' + label + '</div>'
        + count_str +
        '</div>'
    )


def render_property_types(lang="en"):
    """Render property type cards — 6 in a row."""
    title_ar = "🏢 أنواع العقارات"
    title_en = "🏢 Property Types"
    sub_ar = "اختار نوع العقار — بعض الأنواع تقديرية"
    sub_en = "Choose property type — some are market-based estimates"

    title = title_ar if lang == "ar" else title_en
    sub = sub_ar if lang == "ar" else sub_en

    header = (
        '<div style="margin:32px 0 16px 0;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<div style="font-size:26px;">🏢</div>'
        '<div>'
        '<div style="font-size:20px;font-weight:900;color:#1f2937;">'
        + title + '</div>'
        '<div style="font-size:12px;color:#6b7280;margin-top:2px;">'
        + sub + '</div>'
        '</div></div></div>'
    )
    st.markdown(header, unsafe_allow_html=True)

    cols = st.columns(6)
    for i, ptype in enumerate(PROPERTY_TYPES):
        with cols[i]:
            html = _card_html(
                ptype["icon"],
                ptype["ar"] if lang == "ar" else ptype["key"],
                ptype["count"],
                ptype["color"],
                ptype["count"] > 0,
                ptype["note_ar"] if lang == "ar" else ptype["note_en"],
            )
            st.markdown(html, unsafe_allow_html=True)
