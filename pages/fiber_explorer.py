"""Fiber Explorer page."""



from components.page_layout import render_page_header, render_workspace


def render() -> None:
    """Render the Fiber Explorer page."""
    render_page_header(
        title="Fiber Explorer",
        caption="Inspect the building blocks of an optical fiber.",
        description=(
            "Explore fiber geometry, refractive indices, "
            "and the conditions that allow light to travel through an optical fiber."
        ),
    )

    render_workspace(
        "Interactive fiber exploration tools are coming soon."
    )