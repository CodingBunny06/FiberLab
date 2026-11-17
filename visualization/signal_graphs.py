"""Plotly visualizations for attenuation and pulse propagation."""

from __future__ import annotations

import plotly.graph_objects as go


def create_attenuation_figure(
    distance_km: list[float], power_mw: list[float]
) -> go.Figure:
    """Plot optical power versus distance."""
    if len(distance_km) != len(power_mw) or len(distance_km) < 2:
        raise ValueError(
            "Distance and power arrays must have equal lengths of at least two."
        )
    fig = go.Figure(
        go.Scatter(x=distance_km, y=power_mw, mode="lines", name="Optical power")
    )
    fig.update_layout(
        title="Optical Power Attenuation",
        xaxis_title="Fiber length (km)",
        yaxis_title="Power (mW)",
        template="plotly_white",
    )
    return fig


def create_signal_waveform_figure(
    input_signal: list[float], output_signal: list[float], time_axis: list[float]
) -> go.Figure:
    """Compare input and broadened output pulse waveforms."""
    if (
        not (len(time_axis) == len(input_signal) == len(output_signal))
        or len(time_axis) < 2
    ):
        raise ValueError(
            "Time and waveform arrays must have equal lengths of at least two."
        )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=time_axis, y=input_signal, mode="lines", name="Input pulse")
    )
    fig.add_trace(
        go.Scatter(x=time_axis, y=output_signal, mode="lines", name="Output pulse")
    )
    fig.update_layout(
        title="Signal Propagation and Pulse Broadening",
        xaxis_title="Time (s)",
        yaxis_title="Normalized amplitude",
        template="plotly_white",
    )
    return fig
