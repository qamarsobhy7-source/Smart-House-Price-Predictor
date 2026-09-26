"""Quick filter chips — like Property Finder."""
import streamlit as st


def render_quick_filters(lang="en"):
    """Render quick filter chips — 3 rows."""
    if lang == "ar":
        title = "🎛️ فلاتر سريعة"
        subtitle = "اختار نطاق السعر أو المساحة أو الغرف"
        price_chips = [
            ("💰 أقل من 5M", "p_under5"),
            ("💰 5M - 10M", "p_5to10"),
            ("💰 فوق 10M", "p_over10"),
        ]
        size_chips = [
            ("📐 أقل من 100م²", "s_under100"),
            ("📐 100 - 200م²", "s_100to200"),
            ("📐 فوق 200م²", "s_over200"),
        ]
        rooms_chips = [
            ("🛏️ 1-2 غرف", "r_1to2"),
            ("🛏️ 3-4 غرف", "r_3to4"),
            ("🛏️ 5+ غرف", "r_5plus"),
        ]
    else:
        title = "🎛️ Quick Filters"
        subtitle = "Pick a price range, size, or rooms"
        price_chips = [
            ("💰 Under 5M", "p_under5"),
            ("💰 5M - 10M", "p_5to10"),
            ("💰 Over 10M", "p_over10"),
        ]
        size_chips = [
            ("📐 Under 100m²", "s_under100"),
            ("📐 100-200m²", "s_100to200"),
            ("📐 Over 200m²", "s_over200"),
        ]
        rooms_chips = [
            ("🛏️ 1-2 BD", "r_1to2"),
            ("🛏️ 3-4 BD", "r_3to4"),
            ("🛏️ 5+ BD", "r_5plus"),
        ]

    # Header
    header = (
        '<div style="margin:28px 0 14px 0;">'
        '<div style="display:flex;align-items:center;gap:10px;">'
        '<div style="font-size:24px;">🎛️</div>'
        '<div>'
        '<div style="font-size:18px;font-weight:900;color:#1f2937;">'
        + title + '</div>'
        '<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
        + subtitle + '</div>'
        '</div></div></div>'
    )
    st.markdown(header, unsafe_allow_html=True)

    # Row 1 — Price
    for chips in [price_chips, size_chips, rooms_chips]:
        cols = st.columns(3)
        for i, (label, key) in enumerate(chips):
            with cols[i]:
                st.button(label, key=f"chip_{key}", use_container_width=True)
        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
