"""Interactive optical fiber geometry and ray explorer."""
from __future__ import annotations

import math

import streamlit as st

from physics.fiber_geometry import simulate_fiber_ray
from physics.numerical_aperture import (
    calculate_acceptance_angle,
    calculate_critical_angle,
    calculate_numerical_aperture,
)
from visualization.fiber_animation import create_fiber_ray_figure


def render() -> None:
    """Render the fiber ray experiment."""
    st.title("Fiber Explorer")
    st.caption("Explore step-index fiber geometry, numerical aperture and total internal reflection.")
    c1, c2, c3 = st.columns(3)
    with c1:
        n_core = st.number_input("Core refractive index", min_value=1.01, max_value=2.0, value=1.48, step=0.01)
    with c2:
        n_clad = st.number_input("Cladding refractive index", min_value=1.0, max_value=1.99, value=1.46, step=0.01)
    with c3:
        angle = st.slider("Launch angle (degrees)", 0.0, 30.0, 8.0, 0.5)
    if n_core <= n_clad:
        st.error("Core refractive index must be greater than cladding refractive index.")
        return
    try:
        na = calculate_numerical_aperture(n_core, n_clad)
        acceptance = calculate_acceptance_angle(n_core, n_clad)
        critical = calculate_critical_angle(n_core, n_clad)
        ray_data = simulate_fiber_ray(n_core, n_clad, launch_angle_deg=angle)
        st.subheader("Calculated fiber properties")
        a, b, c = st.columns(3)
        a.metric("Numerical aperture", f"{na:.4f}")
        b.metric("Acceptance angle", f"{math.degrees(acceptance):.2f}°")
        c.metric("Critical angle", f"{math.degrees(critical):.2f}°")
        st.plotly_chart(create_fiber_ray_figure(ray_data), use_container_width=True)
        st.success("Guided propagation (TIR condition met)." if ray_data["is_tir"] else "Launch angle exceeds acceptance: ray escapes the core.")
    except ValueError as exc:
        st.error(str(exc))
