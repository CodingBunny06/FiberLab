"""Interactive Gaussian pulse propagation laboratory."""
from __future__ import annotations

import numpy as np
import streamlit as st

from physics.signal_propagation import broaden_gaussian_pulse
from visualization.signal_graphs import create_signal_waveform_figure


def render() -> None:
    st.title("Signal Propagation")
    st.caption("Explore how group-velocity dispersion broadens a Gaussian pulse.")
    c1, c2, c3 = st.columns(3)
    with c1:
        width_ps = st.number_input("Input RMS pulse width (ps)", min_value=1.0, value=20.0, step=1.0)
    with c2:
        beta2 = st.number_input("Dispersion parameter β₂ (ps²/km)", value=20.0, step=1.0)
    with c3:
        length = st.number_input("Fiber length (km)", min_value=0.0, value=50.0, step=5.0)
    width_s = width_ps * 1e-12
    beta2_si = beta2 * 1e-24
    time_ps = np.linspace(-6 * width_ps, 6 * width_ps, 800)
    time_s = (time_ps * 1e-12).tolist()
    input_signal = np.exp(-((time_ps) ** 2) / (2 * width_ps**2)).tolist()
    _, output_signal, output_width = broaden_gaussian_pulse(time_s, width_s, beta2_si, length)
    st.metric("Output RMS pulse width", f"{output_width * 1e12:.3f} ps")
    st.plotly_chart(
        create_signal_waveform_figure(time_ps.tolist(), input_signal, output_signal),
        use_container_width=True,
    )
    st.latex(r"\sigma_{out}=\sigma_{in}\sqrt{1+\left(\frac{\beta_2 L}{\sigma_{in}^2}\right)^2}")
    st.caption("Educational second-order-dispersion model for a Gaussian pulse; not a complete optical-link simulator.")
