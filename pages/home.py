"""FiberLab landing page."""

import streamlit as st


def render() -> None:
    """Render the FiberLab landing page."""
    st.title("FiberLab")
    st.subheader("A virtual optical fiber laboratory")
    st.write(
        "FiberLab is a focused engineering workspace for understanding how optical "
        "fiber systems behave. Use the navigation to move between guided laboratory "
        "experiences as the simulator grows."
    )

    st.divider()
    st.markdown("### Version 1.0 capabilities")
    capability_columns = st.columns(3)
    capabilities = (
        (
            capability_columns[0],
            ":material/explore:",
            "Fiber Explorer",
            "Review the geometry and guiding concepts that define an optical fiber.",
        ),
        (
            capability_columns[1],
            ":material/science:",
            "Attenuation Laboratory",
            "A dedicated workspace for investigating optical loss and attenuation.",
        ),
        (
            capability_columns[2],
            ":material/graphic_eq:",
            "Signal Propagation",
            "Explore the concepts behind signal travel, dispersion, and transmission.",
        ),
    )
    for column, icon, title, description in capabilities:
        with column:
            st.markdown(f"#### {icon} {title}")
            st.caption(description)

    st.info(
        "The v1.0 interface establishes the laboratory workflow. Interactive "
        "physics models and visualizations will be added in future iterations."
    )
