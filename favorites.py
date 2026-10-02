"""Favorites module — save properties in session."""
import streamlit as st


def init_favorites():
    """Initialize favorites in session state."""
    if "favorites" not in st.session_state:
        st.session_state.favorites = []


def add_favorite(property_data: dict):
    """Add property to favorites."""
    init_favorites()
    if property_data not in st.session_state.favorites:
        st.session_state.favorites.append(property_data)


def remove_favorite(property_id):
    """Remove property from favorites."""
    init_favorites()
    st.session_state.favorites = [
        f for f in st.session_state.favorites if f.get("id") != property_id
    ]


def get_favorites():
    """Get all favorites."""
    init_favorites()
    return st.session_state.favorites


def is_favorite(property_id) -> bool:
    """Check if property is in favorites."""
    init_favorites()
    return any(f.get("id") == property_id for f in st.session_state.favorites)
