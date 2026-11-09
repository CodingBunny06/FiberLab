"""FiberLab Streamlit application entry point."""

from __future__ import annotations

import streamlit as st

from pages.attenuation_laboratory import render as render_attenuation_laboratory
from pages.fiber_explorer import render as render_fiber_explorer
from pages.signal_propagation import render as render_signal_propagation

PAGE_RENDERERS = {
    "Fiber Explorer": render_fiber_explorer,
    "Attenuation Laboratory": render_attenuation_laboratory,
    "Signal Propagation": render_signal_propagation,
}


def main() -> None:
    """Configure and render the Streamlit application."""
    st.set_page_config(page_title="FiberLab", page_icon="🔬", layout="wide")

    selected_page = st.sidebar.radio("Navigation", tuple(PAGE_RENDERERS.keys()))
    PAGE_RENDERERS[selected_page]()


if __name__ == "__main__":
    main()
