"""Fiber Explorer page."""

import streamlit as st


def render() -> None:
    """Render the Fiber Explorer page."""
    st.title("Fiber Explorer")
    st.write(
        "Use this section to investigate fiber geometry, refractive indices, and guiding conditions."
    )
