"""Fiber ray visualization utilities.

Assumptions due to missing integration contract file:
- ``ray_data`` is provided by the simulation/physics layer with geometry and
  precomputed ray paths.
- This module performs rendering only and does not calculate ray physics.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import plotly.graph_objects as go

RayPath = Mapping[str, Sequence[float]]


def _validate_numeric(value: Any, key: str) -> float:
    if not isinstance(value, (int, float)):
        msg = f"'{key}' must be a numeric value."
        raise TypeError(msg)
    if value <= 0:
        msg = f"'{key}' must be greater than 0."
        raise ValueError(msg)
    return float(value)


def _validate_ray_path(path: Any, key: str) -> RayPath:
    if not isinstance(path, Mapping):
        msg = f"'{key}' must be a mapping with 'x' and 'y' sequences."
        raise TypeError(msg)

    if "x" not in path or "y" not in path:
        msg = f"'{key}' must include 'x' and 'y'."
        raise ValueError(msg)

    x_points = path["x"]
    y_points = path["y"]

    if not isinstance(x_points, Sequence) or isinstance(x_points, (str, bytes)):
        msg = f"'{key}.x' must be a sequence of numeric values."
        raise TypeError(msg)
    if not isinstance(y_points, Sequence) or isinstance(y_points, (str, bytes)):
        msg = f"'{key}.y' must be a sequence of numeric values."
        raise TypeError(msg)
    if len(x_points) != len(y_points):
        msg = f"'{key}.x' and '{key}.y' must have the same length."
        raise ValueError(msg)
    if len(x_points) < 2:
        msg = f"'{key}' must contain at least 2 points."
        raise ValueError(msg)

    for axis_name, points in (("x", x_points), ("y", y_points)):
        if any(not isinstance(value, (int, float)) for value in points):
            msg = f"'{key}.{axis_name}' must contain only numeric values."
            raise TypeError(msg)

    return {"x": [float(v) for v in x_points], "y": [float(v) for v in y_points]}


def create_fiber_ray_figure(ray_data: Mapping[str, Any]) -> go.Figure:
    """Create a Plotly figure visualizing an optical fiber ray path.

    Expected ``ray_data`` keys:
    - core_radius (float > 0)
    - cladding_radius (float > 0 and larger than core_radius)
    - fiber_length (float > 0)
    - incident_ray ({"x": [...], "y": [...]})
    - reflected_rays (list of {"x": [...], "y": [...]})

    Optional metadata keys used only for annotation:
    - core_refractive_index, cladding_refractive_index, incident_angle_deg
    """

    if not isinstance(ray_data, Mapping):
        msg = "'ray_data' must be a mapping."
        raise TypeError(msg)

    required_keys = (
        "core_radius",
        "cladding_radius",
        "fiber_length",
        "incident_ray",
        "reflected_rays",
    )
    missing = [key for key in required_keys if key not in ray_data]
    if missing:
        msg = f"'ray_data' missing required keys: {', '.join(missing)}"
        raise ValueError(msg)

    core_radius = _validate_numeric(ray_data["core_radius"], "core_radius")
    cladding_radius = _validate_numeric(ray_data["cladding_radius"], "cladding_radius")
    fiber_length = _validate_numeric(ray_data["fiber_length"], "fiber_length")

    if cladding_radius <= core_radius:
        msg = "'cladding_radius' must be larger than 'core_radius'."
        raise ValueError(msg)

    incident_ray = _validate_ray_path(ray_data["incident_ray"], "incident_ray")

    reflected_rays_raw = ray_data["reflected_rays"]
    if not isinstance(reflected_rays_raw, Sequence) or isinstance(
        reflected_rays_raw,
        (str, bytes),
    ):
        msg = "'reflected_rays' must be a sequence of ray-path mappings."
        raise TypeError(msg)

    reflected_rays = [
        _validate_ray_path(path, f"reflected_rays[{idx}]")
        for idx, path in enumerate(reflected_rays_raw)
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=[0, fiber_length, fiber_length, 0, 0],
            y=[
                -cladding_radius,
                -cladding_radius,
                cladding_radius,
                cladding_radius,
                -cladding_radius,
            ],
            fill="toself",
            mode="lines",
            line={"width": 0},
            fillcolor="rgba(173, 216, 230, 0.45)",
            name="Cladding",
            hoverinfo="skip",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[0, fiber_length, fiber_length, 0, 0],
            y=[-core_radius, -core_radius, core_radius, core_radius, -core_radius],
            fill="toself",
            mode="lines",
            line={"width": 0},
            fillcolor="rgba(255, 165, 0, 0.55)",
            name="Core",
            hoverinfo="skip",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=incident_ray["x"],
            y=incident_ray["y"],
            mode="lines+markers",
            marker={"size": 5},
            line={"color": "#d62728", "width": 3, "dash": "dash"},
            name="Incident Ray",
        )
    )

    for idx, reflected_ray in enumerate(reflected_rays):
        figure.add_trace(
            go.Scatter(
                x=reflected_ray["x"],
                y=reflected_ray["y"],
                mode="lines+markers",
                marker={"size": 5},
                line={"color": "#1f77b4", "width": 2},
                name="Reflected Ray" if idx == 0 else f"Reflected Ray {idx + 1}",
                showlegend=idx == 0,
            )
        )

    annotation_fields = {
        "core_refractive_index": "n₁",
        "cladding_refractive_index": "n₂",
        "incident_angle_deg": "θᵢ (deg)",
    }
    annotation_text = "<br>".join(
        f"{label}: {ray_data[field]}"
        for field, label in annotation_fields.items()
        if field in ray_data
    )

    figure.update_layout(
        title="Optical Fiber Ray Simulation",
        xaxis_title="Fiber Length (arb. units)",
        yaxis_title="Radial Position (arb. units)",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        margin={"l": 50, "r": 40, "t": 70, "b": 50},
    )

    figure.update_yaxes(range=[-cladding_radius * 1.1, cladding_radius * 1.1])

    if annotation_text:
        figure.add_annotation(
            x=fiber_length,
            y=cladding_radius * 1.08,
            xanchor="right",
            yanchor="bottom",
            showarrow=False,
            align="right",
            text=annotation_text,
        )

    return figure
