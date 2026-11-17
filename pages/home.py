"""FiberLab landing page."""
import streamlit as st


def render() -> None:
    """Render the FiberLab landing page."""
    st.title("FiberLab")
    st.subheader("Interactive Physics & Optical Fiber Simulation Laboratory")
    st.markdown(
        "Explore interactive experiments that connect mathematical models "
        "with scientific visualization."
    )
    st.divider()
    st.markdown("### Explore the Laboratory")
    capabilities = [
        ("🔭 Fiber Explorer", "Visualize guided and escaping rays; calculate NA, acceptance angle and critical angle."),
        ("〰️ De Broglie Matter Waves", "Explore matter-wave wavelength, momentum and the wave nature of particles."),
        ("📉 Attenuation Laboratory", "Calculate optical power loss and inspect power against fiber length."),
        ("〰️ Signal Propagation", "Compare Gaussian input and output pulses under a simple dispersion model."),
    ]
    columns = st.columns(2)
    for column, (title, description) in zip(columns, capabilities):
        with column, st.container(border=True):
            st.markdown(f"#### {title}")
            st.write(description)
    st.divider()
    st.markdown("### About FiberLab")
    st.write(
        "FiberLab is an educational engineering platform. Its optical-fiber "
        "laboratories and De Broglie matter-wave experiment are separate "
        "physics modules within one application."
    )
    st.info("Development build — verify each experiment and its assumptions before academic use.")
    st.caption("FiberLab | Interactive Physics Simulation Laboratory")
