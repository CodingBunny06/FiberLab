"""Attenuation Laboratory page."""

from components.page_layout import render_page_header, render_workspace


def render() -> None:
    """Render the Attenuation Laboratory page."""
    render_page_header(
        title="Attenuation Laboratory",
        caption="Investigate how optical loss shapes a transmission system.",
        description=(
            "Study optical power loss, attenuation profiles, "
            "and their impact on signal strength over fiber length."
        ),
    )

    render_workspace(
        "Interactive attenuation tools are coming soon."
    )