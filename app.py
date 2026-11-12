"""FiberLab Streamlit application entry point."""

from __future__ import annotations

import streamlit as st

from pages.attenuation_laboratory import render as render_attenuation_laboratory
from pages.fiber_explorer import render as render_fiber_explorer
from pages.guardian_dashboard import render as render_guardian
from pages.home import render as render_home
from pages.signal_propagation import render as render_signal_propagation

PAGE_DEFINITIONS = (
    {
        "render": render_home,
        "title": "FiberLab",
        "icon": ":material/home:",
        "url_path": "home",
        "default": True,
    },
    {
        "render": render_fiber_explorer,
        "title": "Fiber Explorer",
        "icon": ":material/explore:",
        "url_path": "fiber-explorer",
    },
    {
        "render": render_attenuation_laboratory,
        "title": "Attenuation Laboratory",
        "icon": ":material/science:",
        "url_path": "attenuation-laboratory",
    },
    {
        "render": render_signal_propagation,
        "title": "Signal Propagation",
        "icon": ":material/graphic_eq:",
        "url_path": "signal-propagation",
    },
    {
        "render": render_guardian,
        "title": "Guardian",
        "icon": ":material/shield:",
        "url_path": "guardian",
    },
)


def build_navigation():
    """Build the native Streamlit navigation entries."""
    return st.navigation(
        [
            st.Page(
                definition["render"],
                title=definition["title"],
                icon=definition["icon"],
                url_path=definition["url_path"],
                default=definition.get("default", False),
            )
            for definition in PAGE_DEFINITIONS
        ],
        position="sidebar",
    )


def main() -> None:
    """Configure and render the Streamlit application."""
    st.set_page_config(page_title="FiberLab", page_icon="🔬", layout="wide")

    navigation = build_navigation()
    navigation.run()


if __name__ == "__main__":
    main()
