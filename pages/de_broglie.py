"""Interactive De Broglie matter-wave laboratory."""
from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from physics.de_broglie import (
    SPEED_OF_LIGHT,
    de_broglie_wavelength,
    momentum,
)


PARTICLES = {
    "Electron": 9.1093837e-31,
    "Proton": 1.6726219e-27,
    "Neutron": 1.6749275e-27,
    "Custom particle": 1.0e-30,
}


def render() -> None:
    st.title("De Broglie Matter Waves")
    st.caption("Aim: Visualize the wave nature of matter and explore the De Broglie hypothesis.")
    st.markdown("Every moving particle has an associated wavelength, given by **λ = h / p = h / (mv)** for non-relativistic speeds.")
    left, right = st.columns(2)
    with left:
        particle = st.selectbox("Particle", list(PARTICLES))
        mass = PARTICLES[particle]
        if particle == "Custom particle":
            mass = st.number_input("Particle mass (kg)", min_value=1e-36, max_value=1e-20, value=1e-30, format="%.3e")
        velocity = st.number_input("Particle velocity (m/s)", min_value=1.0, max_value=2.9e8, value=1.0e6, step=1.0e5, format="%.3e")
        amplitude = st.slider("Wave amplitude (visual scale)", 0.2, 1.0, 0.75, 0.05)
    wavelength = de_broglie_wavelength(mass, velocity)
    p = momentum(mass, velocity)
    with right:
        st.metric("De Broglie wavelength", f"{wavelength:.4e} m")
        st.metric("Momentum", f"{p:.4e} kg·m/s")
        st.metric("Velocity / speed of light", f"{velocity / SPEED_OF_LIGHT:.3%}")
        if velocity > 0.1 * SPEED_OF_LIGHT:
            st.warning("The non-relativistic approximation becomes less accurate above 0.1c.")
    st.divider()
    st.subheader("Matter-wave visualization")
    # Display a normalized illustrative wave over four wavelengths; x-axis is scaled in units of λ.
    x = np.linspace(0, 4 * wavelength, 800)
    psi = amplitude * np.cos(2 * math.pi * x / wavelength)
    fig = go.Figure(go.Scatter(x=x / wavelength, y=psi, mode="lines", name="Matter wave"))
    fig.update_layout(title="Illustrative De Broglie Wave", xaxis_title="Position (wavelengths, x/λ)", yaxis_title="Relative wave amplitude", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The plotted sinusoid illustrates periodicity; it is not a literal trajectory of the particle.")
    st.subheader("How momentum changes wavelength")
    velocities = np.geomspace(max(velocity / 100, 1), min(velocity * 100, 2.9e8), 120)
    wavelengths = [de_broglie_wavelength(mass, float(v)) for v in velocities]
    comparison = go.Figure(go.Scatter(x=velocities, y=wavelengths, mode="lines", name="λ(v)"))
    comparison.update_layout(xaxis_title="Velocity (m/s)", yaxis_title="Wavelength (m)", yaxis_type="log", xaxis_type="log", template="plotly_white", title="Wavelength decreases as momentum increases")
    st.plotly_chart(comparison, use_container_width=True)
    st.info("For a fixed particle mass, increasing velocity increases momentum and decreases the De Broglie wavelength.")
