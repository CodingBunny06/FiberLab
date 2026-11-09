
"""FiberLab landing page."""

import streamlit as st


def render() -> None:
    """Render the FiberLab landing page."""

    st.title("FiberLab")
    st.subheader("Interactive Optical Fiber Communication Simulator")

    st.markdown(
        """
        Explore the science behind optical fiber communication
        through interactive experiments, mathematical models,
        and scientific visualizations.
        """
    )

    st.divider()

    st.markdown("### Explore the Laboratory")

    capabilities = [
    (
        "🔭 Fiber Explorer",
        (
            "Understand optical fiber geometry, refractive indices, "
            "numerical aperture, acceptance angle, and total internal reflection."
        ),
    ),
    (
        "📉 Attenuation Laboratory",
        (
            "Investigate optical power loss over fiber length and "
            "study how attenuation affects signal strength."
        ),
    ),
    (
        "〰️ Signal Propagation",
        (
            "Explore signal transmission, waveform behaviour, "
            "and the fundamentals of pulse broadening."
        ),
    ),
    ]

    columns = st.columns(3)

    for column, (title, description) in zip(columns, capabilities):
        with column, st.container(border=True):
         st.markdown(f"#### {title}")
         st.write(description)

    st.divider()

    st.markdown("### About FiberLab")

    st.write(
        """
        FiberLab is an educational engineering platform designed
        to make optical fiber concepts easier to understand.

        Our goal is to connect theoretical physics with practical
        simulation through calculations, graphs, and interactive
        laboratory experiences.
        """
    )

    st.info(
        "🚧 Version 1.0 — Under Development. "
        "Core physics models and interactive simulations are being built."
    )

    st.caption("FiberLab | Optical Fiber Communication Laboratory")
