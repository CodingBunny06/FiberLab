"""Interactive De Broglie matter-wave laboratory."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from physics.de_broglie import (
    SPEED_OF_LIGHT,
    de_broglie_wavelength,
    momentum,
)
from visualization.matter_wave import (
    MAX_RENDERED_CYCLES,
    create_matter_wave_figure,
)

PARTICLES = {
    "Electron": 9.1093837e-31,
    "Proton": 1.6726219e-27,
    "Neutron": 1.6749275e-27,
    "Custom particle": 1.0e-30,
}
COMPARISON_PARTICLES = {
    name: mass for name, mass in PARTICLES.items() if name != "Custom particle"
}


def render() -> None:
    st.title("De Broglie Matter Waves")
    st.caption(
        "Aim: Visualize the wave nature of matter and explore the De Broglie hypothesis."
    )
    st.markdown(
        "Every moving particle has an associated wavelength, given by "
        "**λ = h / p = h / (mv)** for non-relativistic speeds."
    )
    left, right = st.columns(2)
    with left:
        particle = st.selectbox("Particle", list(PARTICLES))
        mass = PARTICLES[particle]
        if particle == "Custom particle":
            mass = st.number_input(
                "Particle mass (kg)",
                min_value=1e-36,
                max_value=1e-20,
                value=1e-30,
                format="%.3e",
            )
        velocity = st.number_input(
            "Particle velocity (m/s)",
            min_value=1.0,
            max_value=2.9e8,
            value=1.0e6,
            step=1.0e5,
            format="%.3e",
        )
        amplitude = st.slider("Wave amplitude (visual scale)", 0.2, 1.0, 0.75, 0.05)
        plot_window_nm = st.number_input(
            "Physical plot window (nm)",
            min_value=0.001,
            max_value=1000.0,
            value=1.0,
            step=0.1,
            format="%.3f",
            help=(
                "The horizontal axis is a real distance, not a wavelength-normalized "
                "axis. Reduce this window to resolve very short wavelengths."
            ),
        )

    wavelength = de_broglie_wavelength(mass, velocity)
    particle_momentum = momentum(mass, velocity)
    with right:
        st.metric("De Broglie wavelength", f"{wavelength:.4e} m")
        st.metric("Momentum", f"{particle_momentum:.4e} kg·m/s")
        st.metric("Velocity / speed of light", f"{velocity / SPEED_OF_LIGHT:.3%}")
        if velocity > 0.1 * SPEED_OF_LIGHT:
            st.warning(
                "The non-relativistic approximation becomes less accurate above 0.1c."
            )

    st.divider()
    st.subheader("Matter-wave visualization")
    cycles_in_window = plot_window_nm * 1e-9 / wavelength
    st.caption(
        f"Physical distance shown: {plot_window_nm:g} nm · "
        f"Expected wave cycles: {cycles_in_window:,.2f}"
    )
    if cycles_in_window > MAX_RENDERED_CYCLES:
        st.warning(
            f"This window contains more than {MAX_RENDERED_CYCLES:,} cycles, "
            "which is too dense to render accurately. Reduce the physical plot "
            "window or particle velocity."
        )
    else:
        wave_figure = create_matter_wave_figure(
            wavelength, plot_window_nm, amplitude
        )
        st.plotly_chart(wave_figure, use_container_width=True)
    st.caption(
        "The sinusoid illustrates spatial periodicity; it is not a particle "
        "trajectory or a complete quantum wavefunction."
    )

    st.subheader("Wavelength comparison at the selected velocity")
    comparison_names = list(COMPARISON_PARTICLES)
    comparison_wavelengths_nm = [
        de_broglie_wavelength(COMPARISON_PARTICLES[name], velocity) * 1e9
        for name in comparison_names
    ]
    comparison = go.Figure(
        go.Bar(
            x=comparison_names,
            y=comparison_wavelengths_nm,
            text=[f"{value:.3e} nm" for value in comparison_wavelengths_nm],
            textposition="outside",
            name="Wavelength",
        )
    )
    comparison.update_layout(
        title=f"Electron, proton and neutron at {velocity:.3e} m/s",
        xaxis_title="Particle",
        yaxis_title="De Broglie wavelength (nm, logarithmic scale)",
        yaxis_type="log",
        template="plotly_white",
    )
    st.plotly_chart(comparison, use_container_width=True)

    st.subheader("How momentum changes wavelength")
    velocities = np.geomspace(
        max(velocity / 100, 1), min(velocity * 100, 2.9e8), 120
    )
    wavelengths = [de_broglie_wavelength(mass, float(v)) for v in velocities]
    velocity_figure = go.Figure(
        go.Scatter(x=velocities, y=wavelengths, mode="lines", name="λ(v)")
    )
    velocity_figure.update_layout(
        xaxis_title="Velocity (m/s)",
        yaxis_title="Wavelength (m)",
        yaxis_type="log",
        xaxis_type="log",
        template="plotly_white",
        title="Wavelength decreases as momentum increases",
    )
    st.plotly_chart(velocity_figure, use_container_width=True)
    st.info(
        "At fixed particle mass, increasing velocity increases momentum and "
        "decreases the De Broglie wavelength. At the same velocity, heavier "
        "particles have shorter wavelengths."
    )
