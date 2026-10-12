
"""
UI Components Library - Nawy + Aqarmap inspired
"""
import streamlit as st


def property_card(title, location, price, image_url, badge=None, beds=None, baths=None, area=None, key=None):
    badge_html = ('<div class="card-badge">' + badge + '</div>') if badge else ''
    meta_parts = []
    if beds: meta_parts.append(str(beds) + " Beds")
    if baths: meta_parts.append(str(baths) + " Baths")
    if area: meta_parts.append(str(area) + " sqm")
    meta_html = " &middot; ".join(meta_parts)
    html = (
        '<div class="property-card-nawy">'
        '<div class="property-card-img-wrap">'
        '<img src="' + image_url + '" alt="' + title + '">'
        + badge_html +
        '<div class="property-overlay">'
        '<div class="property-overlay-title">' + title + '</div>'
        '<div class="property-overlay-location">' + location + '</div>'
        '<div class="property-overlay-price">' + price + '</div>'
        '<div class="property-overlay-meta">' + meta_html + '</div>'
        '</div></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def number_pills(label, options, key, default_idx=0):
    if f"{key}_val" not in st.session_state:
        st.session_state[f"{key}_val"] = options[default_idx]
    st.markdown(f'<div class="pills-label">{label}</div>', unsafe_allow_html=True)
    cols = st.columns(len(options))
    for i, opt in enumerate(options):
        with cols[i]:
            is_active = st.session_state[f"{key}_val"] == opt
            if st.button(str(opt), key=f"{key}_{i}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state[f"{key}_val"] = opt
                st.rerun()
    return st.session_state[f"{key}_val"]


def multi_pills(label, options, key, cols_per_row=4):
    if f"{key}_selected" not in st.session_state:
        st.session_state[f"{key}_selected"] = []
    st.markdown(f'<div class="pills-label">{label}</div>', unsafe_allow_html=True)
    selected = st.session_state[f"{key}_selected"]
    for row_start in range(0, len(options), cols_per_row):
        row_options = options[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, opt in enumerate(row_options):
            with cols[i]:
                is_active = opt in selected
                if st.button(opt, key=f"{key}_{row_start + i}", use_container_width=True, type="primary" if is_active else "secondary"):
                    if is_active:
                        selected.remove(opt)
                    else:
                        selected.append(opt)
                    st.session_state[f"{key}_selected"] = selected
                    st.rerun()
    return st.session_state[f"{key}_selected"]


def single_pills(label, options, key, default=None, cols_per_row=4):
    if f"{key}_val" not in st.session_state:
        st.session_state[f"{key}_val"] = default or options[0]
    st.markdown(f'<div class="pills-label">{label}</div>', unsafe_allow_html=True)
    selected = st.session_state[f"{key}_val"]
    for row_start in range(0, len(options), cols_per_row):
        row_options = options[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, opt in enumerate(row_options):
            with cols[i]:
                is_active = selected == opt
                if st.button(opt, key=f"{key}_{row_start + i}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state[f"{key}_val"] = opt
                    st.rerun()
    return st.session_state[f"{key}_val"]


def area_circle_card(name, count, image_url, key):
    st.markdown(f"""
    <div class="area-circle-card">
        <div class="area-circle-img"><img src="{image_url}" alt="{name}"></div>
        <div class="area-circle-name">{name}</div>
        <div class="area-circle-count">{count} كمبوند</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, icon="✨", show_more_text="أظهر المزيد", key=None):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="section-header-custom"><span class="section-header-icon">{icon}</span><h3 class="section-header-title">{title}</h3></div>', unsafe_allow_html=True)
    with col2:
        if key and st.button(show_more_text, key=f"more_{key}", use_container_width=True):
            return True
    return False


def search_button(count=None, key="search"):
    text = f"🔍 ابحث ({count:,})" if count else "🔍 ابحث"
    return st.button(text, key=key, use_container_width=True, type="primary")


def promo_banner(title, subtitle, cta_text, gradient="blue"):
    st.markdown(f"""
    <div class="promo-banner promo-{gradient}">
        <div class="promo-content">
            <div class="promo-title">{title}</div>
            <div class="promo-subtitle">{subtitle}</div>
            <div class="promo-cta">{cta_text} →</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def recommendation_card(title, image_url, delivery_year, key):
    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-img-wrap">
            <img src="{image_url}" alt="{title}">
            <div class="rec-actions">
                <span class="rec-action-btn">❤️</span>
                <span class="rec-action-btn">📤</span>
                <span class="rec-action-btn">🏠</span>
            </div>
            <div class="rec-delivery">التسليم في {delivery_year}</div>
        </div>
        <div class="rec-body"><div class="rec-title">{title}</div></div>
    </div>
    """, unsafe_allow_html=True)


def stat_card(icon, value, label, color="primary"):
    st.markdown(f"""
    <div class="stat-card stat-{color}">
        <div class="stat-card-icon">{icon}</div>
        <div class="stat-card-value">{value}</div>
        <div class="stat-card-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)
