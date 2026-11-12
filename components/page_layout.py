"""Reusable page layout components for FiberLab."""

import streamlit as st


def render_page_header(title: str, caption: str, description: str) -> None:
    """Render a consistent header across laboratory pages."""
    st.title(title)
    st.caption(caption)
    st.write(description)
    st.divider()


def render_workspace(message: str) -> None:
    """Render a standard laboratory workspace section."""
    st.subheader("Laboratory workspace")
    st.info(message)
