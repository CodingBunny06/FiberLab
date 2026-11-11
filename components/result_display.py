
"""Reusable result display components for FiberLab."""

import streamlit as st


def render_result_metrics(results: dict[str, str]) -> None:
    """Display simulation results as a row of metrics."""
    if not results:
        st.info("No simulation results available yet.")
        return

    columns = st.columns(len(results))

    for column, (label, value) in zip(columns, results.items()):
        with column:
            st.metric(label=label, value=value)
