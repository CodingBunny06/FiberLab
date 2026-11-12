"""Signal Propagation page."""

from components.page_layout import render_page_header, render_workspace


def render() -> None:
    """Render the Signal Propagation page."""
    render_page_header(
        title="Signal Propagation",
        caption="Follow the journey of an optical signal through the fiber.",
        description=(
            "Explore signal transmission, waveform behaviour, "
            "and the fundamentals of pulse broadening and dispersion."
        ),
    )

    render_workspace("Interactive signal propagation tools are coming soon.")
