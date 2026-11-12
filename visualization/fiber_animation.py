"""Optical fiber ray propagation visualization module for FiberLab.

This module strictly separates visualization from physics computations.
All ray trajectory coordinates, angles, and reflection classifications must be
pre-computed by the physics/simulation layer and passed via ``ray_data``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import plotly.graph_objects as go

REQUIRED_KEYS: frozenset[str] = frozenset(
    {
        "core_radius",
        "cladding_radius",
        "fiber_length",
        "incident_ray",
        "propagating_ray",
        "is_tir",
    }
)


def _extract_xy(
    points: Mapping[str, Sequence[float]] | Sequence[Sequence[float]],
    field_name: str,
) -> tuple[list[float], list[float]]:
    """Validate and extract (x, y) coordinate lists from a dict or point list."""
    if isinstance(points, Mapping):
        if "x" not in points or "y" not in points:
            msg = f"'{field_name}' mapping must contain both 'x' and 'y' keys."
            raise ValueError(msg)
        x_vals = [float(v) for v in points["x"]]
        y_vals = [float(v) for v in points["y"]]
    elif isinstance(points, Sequence) and not isinstance(points, (str, bytes)):
        if len(points) == 0:
            msg = f"'{field_name}' must contain at least 2 points."
            raise ValueError(msg)
        try:
            x_vals = [float(pt[0]) for pt in points]
            y_vals = [float(pt[1]) for pt in points]
        except (TypeError, IndexError, ValueError) as exc:
            msg = f"'{field_name}' sequence elements must be (x, y) coordinate pairs."
            raise ValueError(msg) from exc
    else:
        msg = f"'{field_name}' must be a mapping with 'x'/'y' or a sequence of (x, y) pairs."
        raise TypeError(msg)

    if len(x_vals) != len(y_vals):
        msg = f"'{field_name}' x and y coordinate sequences must have equal length."
        raise ValueError(msg)
    if len(x_vals) < 2:
        msg = f"'{field_name}' must contain at least 2 coordinate points."
        raise ValueError(msg)

    return x_vals, y_vals


def validate_ray_data(ray_data: Mapping[str, Any]) -> None:
    """Validate the input contract for ``create_fiber_ray_figure``.

    Raises:
        TypeError: If ``ray_data`` is not a mapping or contains invalid field types.
        ValueError: If required keys are missing or geometric dimensions are invalid.
    """
    if not isinstance(ray_data, Mapping):
        msg = "ray_data must be a mapping (dict) following MODULE_CONTRACTS.md."
        raise TypeError(msg)

    missing = REQUIRED_KEYS - set(ray_data.keys())
    if missing:
        missing_str = ", ".join(sorted(missing))
        msg = f"ray_data is missing required keys: {missing_str}"
        raise ValueError(msg)

    core_radius = float(ray_data["core_radius"])
    cladding_radius = float(ray_data["cladding_radius"])
    fiber_length = float(ray_data["fiber_length"])

    if core_radius <= 0:
        msg = "core_radius must be strictly positive (> 0)."
        raise ValueError(msg)
    if cladding_radius <= core_radius:
        msg = "cladding_radius must be strictly greater than core_radius."
        raise ValueError(msg)
    if fiber_length <= 0:
        msg = "fiber_length must be strictly positive (> 0)."
        raise ValueError(msg)

    if not isinstance(ray_data["is_tir"], bool):
        msg = "is_tir must be a boolean value."
        raise TypeError(msg)

    if "n_core" in ray_data and "n_cladding" in ray_data:
        n_core = float(ray_data["n_core"])
        n_cladding = float(ray_data["n_cladding"])
        if n_core <= 0 or n_cladding <= 0:
            msg = "Refractive indices n_core and n_cladding must be positive (> 0)."
            raise ValueError(msg)

    _extract_xy(ray_data["incident_ray"], "incident_ray")
    _extract_xy(ray_data["propagating_ray"], "propagating_ray")

    if ray_data.get("refracted_ray") is not None:
        _extract_xy(ray_data["refracted_ray"], "refracted_ray")


def create_fiber_ray_figure(ray_data: Mapping[str, Any]) -> go.Figure:
    """Create an interactive Plotly figure depicting optical fiber ray propagation.

    This function performs zero physics calculations and relies entirely on the
    pre-computed coordinates and flags provided in ``ray_data``.

    Args:
        ray_data: Dictionary adhering to the FiberLab visualization contract:
            - ``core_radius`` (float): Radius of the fiber core (> 0).
            - ``cladding_radius`` (float): Outer radius of the fiber cladding (> core_radius).
            - ``fiber_length`` (float): Axial length of the optical fiber (> 0).
            - ``incident_ray`` (dict or sequence): Coordinates ``{"x": [...], "y": [...]}``
              or ``[(x0, y0), ...]`` for the incident launch ray entering the fiber.
            - ``propagating_ray`` (dict or sequence): Coordinates for the reflected
              ray path inside the fiber core.
            - ``is_tir`` (bool): Whether Total Internal Reflection (TIR) occurs.
            - ``refracted_ray`` (optional dict or sequence): Cladding loss ray path when
              ``is_tir`` is False.
            - ``reflection_points`` (optional dict or sequence): Coordinates of bounce points
              at the core-cladding interface.
            - ``n_core`` (optional float): Core refractive index (for annotation only).
            - ``n_cladding`` (optional float): Cladding refractive index (for annotation only).
            - ``incident_angle_deg`` (optional float): Launch angle in degrees (for annotation).
            - ``critical_angle_deg`` (optional float): Critical angle in degrees (for annotation).
            - ``acceptance_angle_deg`` (optional float): Acceptance angle in degrees (for annotation).

    Returns:
        plotly.graph_objects.Figure: Configured interactive 2D optical fiber diagram.
    """
    validate_ray_data(ray_data)

    core_r = float(ray_data["core_radius"])
    clad_r = float(ray_data["cladding_radius"])
    length = float(ray_data["fiber_length"])
    is_tir = bool(ray_data["is_tir"])

    inc_x, inc_y = _extract_xy(ray_data["incident_ray"], "incident_ray")
    prop_x, prop_y = _extract_xy(ray_data["propagating_ray"], "propagating_ray")

    fig = go.Figure()

    # 1. Upper Cladding Region (+core_r to +clad_r)
    fig.add_trace(
        go.Scatter(
            x=[0.0, length, length, 0.0, 0.0],
            y=[core_r, core_r, clad_r, clad_r, core_r],
            fill="toself",
            fillcolor="rgba(148, 163, 184, 0.30)",
            line={"color": "rgba(100, 116, 139, 0.8)", "width": 1.5},
            name="Cladding",
            legendgroup="cladding",
            hoverinfo="skip",
        )
    )

    # 2. Lower Cladding Region (-clad_r to -core_r)
    fig.add_trace(
        go.Scatter(
            x=[0.0, length, length, 0.0, 0.0],
            y=[-clad_r, -clad_r, -core_r, -core_r, -clad_r],
            fill="toself",
            fillcolor="rgba(148, 163, 184, 0.30)",
            line={"color": "rgba(100, 116, 139, 0.8)", "width": 1.5},
            name="Cladding",
            legendgroup="cladding",
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # 3. Core Region (-core_r to +core_r)
    fig.add_trace(
        go.Scatter(
            x=[0.0, length, length, 0.0, 0.0],
            y=[-core_r, -core_r, core_r, core_r, -core_r],
            fill="toself",
            fillcolor="rgba(56, 189, 248, 0.22)",
            line={"color": "rgba(2, 132, 199, 0.95)", "width": 2},
            name="Core",
            hoverinfo="skip",
        )
    )

    # 4. Optical Axis (y = 0)
    fig.add_trace(
        go.Scatter(
            x=[min(0.0, min(inc_x)), length],
            y=[0.0, 0.0],
            mode="lines",
            line={"color": "rgba(71, 85, 105, 0.6)", "width": 1, "dash": "dashdot"},
            name="Optical Axis",
            hoverinfo="skip",
        )
    )

    # 5. Incident Ray Path
    fig.add_trace(
        go.Scatter(
            x=inc_x,
            y=inc_y,
            mode="lines+markers",
            line={"color": "#f59e0b", "width": 3, "dash": "dash"},
            marker={"size": 6, "color": "#f59e0b"},
            name="Incident Ray",
        )
    )

    # 6. Propagating / Reflected Ray Path
    ray_color = "#10b981" if is_tir else "#ef4444"
    ray_label = (
        "Guided Ray (Total Internal Reflection)"
        if is_tir
        else "Partially Reflected Ray ( TIR Failed )"
    )
    fig.add_trace(
        go.Scatter(
            x=prop_x,
            y=prop_y,
            mode="lines+markers",
            line={"color": ray_color, "width": 3, "dash": "solid"},
            marker={"size": 6, "color": ray_color},
            name=ray_label,
        )
    )

    # 7. Optional Refracted / Cladding Loss Ray Path (when TIR fails or provided)
    refracted = ray_data.get("refracted_ray")
    if refracted is not None:
        ref_x, ref_y = _extract_xy(refracted, "refracted_ray")
        fig.add_trace(
            go.Scatter(
                x=ref_x,
                y=ref_y,
                mode="lines",
                line={"color": "#ef4444", "width": 2, "dash": "dot"},
                name="Refracted Loss Ray",
            )
        )

    # 8. Optional Reflection Bounce Markers at Core-Cladding Boundary
    reflection_pts = ray_data.get("reflection_points")
    if reflection_pts is not None:
        rx, ry = _extract_xy(reflection_pts, "reflection_points")
        fig.add_trace(
            go.Scatter(
                x=rx,
                y=ry,
                mode="markers",
                marker={
                    "size": 9,
                    "symbol": "diamond",
                    "color": "#059669" if is_tir else "#dc2626",
                    "line": {"width": 1.5, "color": "#ffffff"},
                },
                name="TIR Reflection Points" if is_tir else "Boundary Hit Points",
            )
        )

    # Build informative subtitle from pre-computed metadata if supplied
    subtitle_parts: list[str] = [
        "Regime: Total Internal Reflection (TIR)"
        if is_tir
        else "Regime: Refraction / Cladding Loss"
    ]
    if "n_core" in ray_data and "n_cladding" in ray_data:
        subtitle_parts.append(
            f"n_core={float(ray_data['n_core']):.3f}, n_clad={float(ray_data['n_cladding']):.3f}"
        )
    if "incident_angle_deg" in ray_data:
        subtitle_parts.append(f"θ_in={float(ray_data['incident_angle_deg']):.1f}°")
    if "acceptance_angle_deg" in ray_data:
        subtitle_parts.append(f"θ_a={float(ray_data['acceptance_angle_deg']):.1f}°")

    subtitle_text = " | ".join(subtitle_parts)

    fig.update_layout(
        title={
            "text": f"Optical Fiber Ray Propagation<br><sup>{subtitle_text}</sup>",
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis={
            "title": "Axial Distance z (µm)",
            "range": [min(-0.15 * length, min(inc_x) * 1.1), length * 1.05],
            "zeroline": True,
            "showgrid": True,
        },
        yaxis={
            "title": "Radial Position r (µm)",
            "range": [-clad_r * 1.25, clad_r * 1.25],
            "zeroline": False,
            "showgrid": True,
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
        },
        template="plotly_white",
        margin={"l": 60, "r": 40, "t": 90, "b": 60},
    )

    return fig
