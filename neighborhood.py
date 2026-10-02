"""Neighborhood insights — local area information."""
import streamlit as st


# Mock data for neighborhoods
NEIGHBORHOOD_DATA = {
    "schools": {"rating": 4.2, "count": 12, "nearest": "2.5 km"},
    "hospitals": {"rating": 4.5, "count": 8, "nearest": "1.8 km"},
    "malls": {"rating": 4.7, "count": 6, "nearest": "3.2 km"},
    "restaurants": {"rating": 4.3, "count": 25, "nearest": "0.5 km"},
    "transport": {"rating": 3.8, "count": 15, "nearest": "1.0 km"},
    "parks": {"rating": 4.0, "count": 4, "nearest": "2.0 km"},
}


def render_neighborhood_info(district: str):
    """Render neighborhood insights."""
    st.markdown(f"### 🏘️ معلومات حي {district}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏫 مدارس", f"{NEIGHBORHOOD_DATA['schools']['count']}", 
                  f"⭐ {NEIGHBORHOOD_DATA['schools']['rating']}")
        st.metric("🏥 مستشفيات", f"{NEIGHBORHOOD_DATA['hospitals']['count']}", 
                  f"⭐ {NEIGHBORHOOD_DATA['hospitals']['rating']}")
    
    with col2:
        st.metric("🛍️ مولات", f"{NEIGHBORHOOD_DATA['malls']['count']}", 
                  f"⭐ {NEIGHBORHOOD_DATA['malls']['rating']}")
        st.metric("🍽️ مطاعم", f"{NEIGHBORHOOD_DATA['restaurants']['count']}", 
                  f"⭐ {NEIGHBORHOOD_DATA['restaurants']['rating']}")
    
    with col3:
        st.metric("🚌 مواصلات", f"{NEIGHBORHOOD_DATA['transport']['count']}", 
                  f"⭐ {NEIGHBORHOOD_DATA['transport']['rating']}")
        st.metric("🌳 حدائق", f"{NEIGHBORHOOD_DATA['parks']['count']}", 
                  f"⭐ {NEIGHBORHOOD_DATA['parks']['rating']}")
