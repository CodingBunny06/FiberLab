"""Plotly visualization helpers for De Broglie matter waves."""

from __future__ import annotations

import math

import plotly.graph_objects as go

MAX_RENDERED_CYCLES = 2_000
POINTS_PER_CYCLE = 40
MINIMUM_SAMPLE_COUNT = 800


def create_matter_wave_figure(
    wavelength_m: float, plot_window_nm: float, amplitude: float
) -> go.Figure:
    """Create a matter wave over a fixed physical distance measured in nm."""
    values = (wavelength_m, plot_window_nm, amplitude)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) <= 0
        for value in values
    ):
        raise ValueError("Wavelength, plot window and amplitude must be positive and finite.")

    window_m = float(plot_window_nm) * 1e-9
    cycles = window_m / float(wavelength_m)
    if cycles > MAX_RENDERED_CYCLES:
        raise ValueError(
            f"Plot window contains more than {MAX_RENDERED_CYCLES} wave cycles."
        )

    sample_count = max(
        MINIMUM_SAMPLE_COUNT, math.ceil(cycles * POINTS_PER_CYCLE) + 1
    )
    x_nm = [
        index * float(plot_window_nm) / (sample_count - 1)
        for index in range(sample_count)
    ]
    wave = [
        float(amplitude)
        * math.cos(2 * math.pi * (position_nm * 1e-9) / float(wavelength_m))
        for position_nm in x_nm
    ]
    figure = go.Figure(
        go.Scatter(x=x_nm, y=wave, mode="lines", name="Matter wave")
    )
    figure.update_layout(
        title="Illustrative De Broglie Wave",
        xaxis_title="Physical position (nm)",
        yaxis_title="Relative wave amplitude",
        template="plotly_white",
    )
    return figure
