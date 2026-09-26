"""Discover section — tabs like Property Finder."""
import streamlit as st
from popular_areas import render_popular_areas
from property_types import render_property_types
from featured_properties import render_featured_properties


def render_discover_section(lang="en"):
    """Render discover section with 3 tabs."""
    if lang == "ar":
        title = "🔍 اكتشف العقارات"
        subtitle = "تصفح حسب النوع أو المنطقة أو العقارات المميزة"
        tab1 = "⭐ مميزة"
        tab2 = "🔥 الأكثر طلباً"
        tab3 = "🏢 الأنواع"
    else:
        title = "🔍 Discover"
        subtitle = "Browse by type, area, or featured properties"
        tab1 = "⭐ Featured"
        tab2 = "🔥 Popular"
        tab3 = "🏢 Types"

    header = (
        '<div style="margin:32px 0 20px 0;padding:24px;'
        'background:linear-gradient(135deg,#f0f9ff 0%,#e0e7ff 100%);'
        'border-radius:20px;">'
        '<div style="font-size:24px;font-weight:900;color:#1f2937;'
        'margin-bottom:4px;">' + title + '</div>'
        '<div style="font-size:13px;color:#6b7280;">' + subtitle + '</div>'
        '</div>'
    )
    st.markdown(header, unsafe_allow_html=True)

    t1, t2, t3 = st.tabs([tab1, tab2, tab3])

    with t1:
        render_featured_properties(lang=lang)
    with t2:
        render_popular_areas(lang=lang)
    with t3:
        render_property_types(lang=lang)
