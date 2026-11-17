"""Interactive optical attenuation laboratory."""

from __future__ import annotations

import numpy as np
import streamlit as st

from physics.attenuation import calculate_output_power, calculate_total_loss
from visualization.signal_graphs import create_attenuation_figure


def render() -> None:
    st.title("Attenuation Laboratory")
    st.caption("Investigate optical power loss over fiber length.")
    a, b, c = st.columns(3)
    with a:
        input_power = st.number_input(
            "Input power (mW)", min_value=0.01, value=1.0, step=0.1
        )
    with b:
        alpha = st.number_input(
            "Attenuation (dB/km)", min_value=0.0, value=0.2, step=0.05
        )
    with c:
        length = st.number_input(
            "Fiber length (km)", min_value=0.01, value=10.0, step=1.0
        )
    output = calculate_output_power(input_power, alpha, length)
    loss = calculate_total_loss(alpha, length)
    x = np.linspace(0, length, 150)
    # At zero distance, no attenuation has occurred; preserve the input power.
    powers = [input_power] + [
        calculate_output_power(input_power, alpha, float(distance))
        for distance in x[1:]
    ]
    m1, m2, m3 = st.columns(3)
    m1.metric("Output power", f"{output:.4f} mW")
    m2.metric("Total loss", f"{loss:.3f} dB")
    m3.metric("Power retained", f"{output / input_power:.1%}")
    st.plotly_chart(
        create_attenuation_figure(x.tolist(), powers), use_container_width=True
    )
    st.latex(r"P_{out}=P_{in}\,10^{-\alpha L/10}")
    st.caption(
        "Idealized attenuation-only model; connector, splice and bending losses are not included."
    )
