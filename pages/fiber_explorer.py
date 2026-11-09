"""Fiber Explorer page."""

import streamlit as st


def render() -> None:
    """Render the Fiber Explorer page."""
    st.title("Fiber Explorer")
    st.caption("Inspect the building blocks of an optical fiber.")
    st.write(
        "This laboratory is reserved for guided exploration of fiber geometry, "
        "refractive indices, and light-guiding conditions."
    )
    st.divider()
    st.subheader("Laboratory workspace")
    st.info("Interactive fiber exploration tools are coming soon.")
