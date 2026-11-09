"""Signal Propagation page."""

import streamlit as st


def render() -> None:
    """Render the Signal Propagation page."""
    st.title("Signal Propagation")
    st.caption("Follow the journey of an optical signal through the fiber.")
    st.write(
        "This laboratory will provide a focused workspace for exploring signal "
        "behavior, dispersion, and transmission distance."
    )
    st.divider()
    st.subheader("Laboratory workspace")
    st.info("Interactive signal propagation tools are coming soon.")
