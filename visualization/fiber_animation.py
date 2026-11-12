"""Optical fiber ray propagation visualization module for FiberLab.

This module strictly separates visualization from physics computations.
All ray trajectory coordinates, angles, and reflection classifications must be
pre-computed by the physics/simulation layer and passed via `ray_data`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
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


def _is_valid_number(value: Any) -> bool:
    """Return True if value is a finite int or float (excluding bool)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


def _validate_ray_points(ray: Any, ray_key: str) -> tuple[list[float], list[float]]:
    """Validate and normalize a ray coordinate structure into (x_list, y_list)."""
    if isinstance(ray, Mapping):
        if "x" not in ray or "y" not in ray:
            raise ValueError(
                f"'{ray_key}' mapping must contain both 'x' and 'y' keys."
            )
        raw_x = ray["x"]
        raw_y = ray["y"]
        if (
            not isinstance(raw_x, Sequence)
            or isinstance(raw_x, (str, bytes))
            or not isinstance(raw_y, Sequence)
            or isinstance(raw_y, (str, bytes))
        ):
            raise ValueError(
                f"'{ray_key}' x and y fields must be sequences of numbers."
            )
        if len(raw_x) != len(raw_y):
            raise ValueError(
                f"'{ray_key}' x and y sequences must have equal length."
            )
        if len(raw_x) < 2:
            raise ValueError(
                f"'{ray_key}' must contain at least 2 coordinate points."
            )
        for coord in (*raw_x, *raw_y):
            if not _is_valid_number(coord):
                raise ValueError(
                    f"'{ray_key}' coordinates must be finite real numbers."
                )
        return [float(v) for v in raw_x], [float(v) for v in raw_y]

    if isinstance(ray, Sequence) and not isinstance(ray, (str, bytes)):
        if len(ray) < 2:
            raise ValueError(
                f"'{ray_key}' must contain at least 2 coordinate points."
            )
        xs: list[float] = []
        ys: list[float] = []
        for pt in ray:
            if (
                not isinstance(pt, Sequence)
                or isinstance(pt, (str, bytes))
                or len(pt) != 2
                or not _is_valid_number(pt[0])
                or not _is_valid_number(pt[1])
            ):
                raise ValueError(
                    f"'{ray_key}' points must be finite (x, y) pairs."
                )
            xs.append(float(pt[0]))
            ys.append(float(pt[1]))
        return xs, ys

    raise ValueError(
        f"'{ray_key}' must be a dict with 'x' and 'y' sequences or a sequence of (x, y) pairs."
    )


def _validate_ray_data(ray_data: Mapping[str, Any]) -> None:
    """Validate the incoming ray_data payload against the module contract."""
    if not isinstance(ray_data, Mapping):
        raise TypeError("ray_data must be a dictionary-like Mapping.")

    missing = REQUIRED_KEYS - set(ray_data.keys())
    if missing:
        raise ValueError(f"Missing required keys in ray_data: {sorted(missing)}")

    for key in ("core_radius", "cladding_radius", "fiber_length"):
        val = ray_data[key]
        if not _is_valid_number(val) or float(val) <= 0:
            raise ValueError(f"'{key}' must be a finite positive number.")

    if float(ray_data["cladding_radius"]) <= float(ray_data["core_radius"]):
        raise ValueError(
            "cladding_radius must be strictly greater than core_radius."
        )

    if not isinstance(ray_data["is_tir"], bool):
        raise ValueError("'is_tir' must be a boolean value.")

    _validate_ray_points(ray_data["incident_ray"], "incident_ray")
    _validate_ray_points(ray_data["propagating_ray"], "propagating_ray")

    # Optional refracted ray validation
    if "refracted_ray" in ray_data and ray_data["refracted_ray"] is not None:
        _validate_ray_points(ray_data["refracted_ray"], "refracted_ray")

    if "refracted_rays" in ray_data and ray_data["refracted_rays"] is not None:
        refracted_rays = ray_data["refracted_rays"]
        if not isinstance(refracted_rays, Sequence) or isinstance(
            refracted_rays, (str, bytes)
        ):
            raise ValueError("'refracted_rays' must be a sequence of ray paths.")
        for idx, r_ray in enumerate(refracted_rays):
            _validate_ray_points(r_ray, f"refracted_rays[{idx}]")

    if (
        "reflection_points" in ray_data
        and ray_data["reflection_points"] is not None
    ):
        pts = ray_data["reflection_points"]
        if isinstance(pts, Mapping):
            if "x" not in pts or "y" not in pts or len(pts["x"]) != len(pts["y"]):
                raise ValueError(
                    "'reflection_points' mapping must have equal-length 'x' and 'y' sequences."
                )
            for coord in (*pts["x"], *pts["y"]):
                if not _is_valid_number(coord):
                    raise ValueError(
                        "'reflection_points' coordinates must be finite numbers."
                    )
        elif isinstance(pts, Sequence) and not isinstance(pts, (str, bytes)):
            for pt in pts:
                if (
                    not isinstance(pt, Sequence)
                    or len(pt) != 2
                    or not _is_valid_number(pt[0])
                    or not _is_valid_number(pt[1])
                ):
                    raise ValueError(
                        "'reflection_points' must contain finite (x, y) pairs."
                    )
        else:
            raise ValueError(
                "'reflection_points' must be a coordinate mapping or sequence of (x, y) pairs."
            )

    # Optional scalar metadata validation
    for opt_key in (
        "n_core",
        "n_cladding",
        "core_refractive_index",
        "cladding_refractive_index",
        "incident_angle_deg",
        "acceptance_angle_deg",
        "critical_angle_deg",
    ):
        if opt_key in ray_data and ray_data[opt_key] is not None:
            if not _is_valid_number(ray_data[opt_key]):
                raise ValueError(
                    f"Optional metadata '{opt_key}' must be a finite real number."
                )

    n_core = ray_data.get("n_core", ray_data.get("core_refractive_index"))
    n_clad = ray_data.get(
        "n_cladding", ray_data.get("cladding_refractive_index")
    )
    if n_core is not None and float(n_core) <= 0:
        raise ValueError("Core refractive index must be positive.")
    if n_clad is not None and float(n_clad) <= 0:
        raise ValueError("Cladding refractive index must be positive.")
    if n_core is not None and n_clad is not None and float(n_core) <= float(n_clad):
        raise ValueError(
            "Core refractive index must be strictly greater than cladding refractive index."
        )


def _add_fiber_structure(
    fig: go.Figure,
    core_r: float,
    clad_r: float,
    length: float,
    inc_x_min: float,
) -> None:
    """Add core, cladding, and interfaces to the Plotly figure."""
    x_min = min(-0.1 * length, inc_x_min * 1.05 if inc_x_min < 0 else -0.1 * length)
    x_max = length

    fig.add_shape(
        type="rect",
        x0=0,
        y0=-clad_r,
        x1=x_max,
        y1=clad_r,
        fillcolor="rgba(220, 235, 252, 0.35)",
        line={"color": "rgba(100, 149, 237, 0.8)", "width": 1.5, "dash": "dot"},
        layer="below",
        name="Cladding Boundary",
    )

    fig.add_shape(
        type="rect",
        x0=0,
        y0=-core_r,
        x1=x_max,
        y1=core_r,
        fillcolor="rgba(173, 216, 230, 0.45)",
        line={"color": "rgba(70, 130, 180, 0.9)", "width": 1.5},
        layer="below",
        name="Core Region",
    )

    fig.add_trace(
        go.Scatter(
            x=[0, x_max],
            y=[core_r, core_r],
            mode="lines",
            line={"color": "steelblue", "width": 1, "dash": "dash"},
            name="Upper Core Interface",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, x_max],
            y=[-core_r, -core_r],
            mode="lines",
            line={"color": "steelblue", "width": 1, "dash": "dash"},
            name="Lower Core Interface",
            showlegend=True,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[x_min, x_max],
            y=[0, 0],
            mode="lines",
            line={"color": "gray", "width": 1, "dash": "dashdot"},
            name="Fiber Optical Axis",
            showlegend=True,
        )
    )


def _extract_reflection_points(
    ray_data: Mapping[str, Any],
    prop_x: list[float],
    prop_y: list[float],
    core_r: float,
) -> tuple[list[float], list[float]]:
    """Extract reflection points from explicit metadata or propagating ray boundary hits."""
    pts = ray_data.get("reflection_points")
    if pts is not None:
        if isinstance(pts, Mapping):
            return [float(v) for v in pts["x"]], [float(v) for v in pts["y"]]
        return [float(p[0]) for p in pts], [float(p[1]) for p in pts]

    bounce_x: list[float] = []
    bounce_y: list[float] = []
    for x, y in zip(prop_x, prop_y):
        if abs(abs(y) - core_r) < 1e-4:
            bounce_x.append(x)
            bounce_y.append(y)
    return bounce_x, bounce_y


def _add_ray_paths(
    fig: go.Figure,
    inc_x: list[float],
    inc_y: list[float],
    prop_x: list[float],
    prop_y: list[float],
    bounce_x: list[float],
    bounce_y: list[float],
    is_tir: bool,
) -> None:
    """Draw incident, internal reflection/refraction, and bounce markers."""
    fig.add_trace(
        go.Scatter(
            x=inc_x,
            y=inc_y,
            mode="lines+markers",
            line={"color": "darkorange", "width": 2.5},
            marker={"size": 4},
            name="Incident Launch Ray",
            hovertemplate="Incident: (z=%{x:.2f} μm, r=%{y:.2f} μm)<extra></extra>",
        )
    )

    prop_color = "crimson" if is_tir else "goldenrod"
    prop_label = "Guided Ray (TIR)" if is_tir else "Attenuated Ray (Refracted)"
    fig.add_trace(
        go.Scatter(
            x=prop_x,
            y=prop_y,
            mode="lines+markers",
            line={"color": prop_color, "width": 2.5},
            marker={"size": 5, "symbol": "circle"},
            name=prop_label,
            hovertemplate="Core Ray: (z=%{x:.2f} μm, r=%{y:.2f} μm)<extra></extra>",
        )
    )

    if bounce_x:
        fig.add_trace(
            go.Scatter(
                x=bounce_x,
                y=bounce_y,
                mode="markers",
                marker={
                    "size": 8,
                    "color": "gold",
                    "symbol": "diamond",
                    "line": {"color": "black", "width": 1},
                },
                name="Interface Reflection Points",
                hovertemplate="Reflection Point: (z=%{x:.2f} μm, r=%{y:.2f} μm)<extra></extra>",
            )
        )


def _add_refracted_rays(
    fig: go.Figure,
    refracted_rays: Sequence[Any],
) -> None:
    """Draw cladding-refracted rays when total internal reflection is not met."""
    for idx, r_ray in enumerate(refracted_rays):
        rx, ry = _validate_ray_points(r_ray, f"refracted_rays[{idx}]")
        fig.add_trace(
            go.Scatter(
                x=rx,
                y=ry,
                mode="lines",
                line={"color": "mediumpurple", "width": 1.8, "dash": "dash"},
                name="Refracted Cladding Loss" if idx == 0 else None,
                showlegend=(idx == 0),
                hovertemplate="Refracted Loss: (z=%{x:.2f} μm, r=%{y:.2f} μm)<extra></extra>",
            )
        )


def create_fiber_ray_figure(ray_data: Mapping[str, Any]) -> go.Figure:
    """Build a complete 2D Plotly Figure illustrating optical fiber ray propagation."""
    _validate_ray_data(ray_data)

    core_r = float(ray_data["core_radius"])
    clad_r = float(ray_data["cladding_radius"])
    length = float(ray_data["fiber_length"])
    inc_x, inc_y = _validate_ray_points(ray_data["incident_ray"], "incident_ray")
    prop_x, prop_y = _validate_ray_points(
        ray_data["propagating_ray"], "propagating_ray"
    )
    is_tir = ray_data["is_tir"]

    refracted_list: list[Any] = []
    if ray_data.get("refracted_ray") is not None:
        refracted_list.append(ray_data["refracted_ray"])
    if ray_data.get("refracted_rays") is not None:
        refracted_list.extend(ray_data["refracted_rays"])

    fig = go.Figure()
    inc_x_min = min(inc_x)

    _add_fiber_structure(
        fig=fig,
        core_r=core_r,
        clad_r=clad_r,
        length=length,
        inc_x_min=inc_x_min,
    )

    bounce_x, bounce_y = _extract_reflection_points(
        ray_data=ray_data,
        prop_x=prop_x,
        prop_y=prop_y,
        core_r=core_r,
    )

    _add_ray_paths(
        fig=fig,
        inc_x=inc_x,
        inc_y=inc_y,
        prop_x=prop_x,
        prop_y=prop_y,
        bounce_x=bounce_x,
        bounce_y=bounce_y,
        is_tir=is_tir,
    )

    if refracted_list:
        _add_refracted_rays(fig, refracted_list)

    subtitle_parts: list[str] = [
        "Regime: Total Internal Reflection (TIR)"
        if is_tir
        else "Regime: Refraction / Cladding Loss"
    ]
    n_core = ray_data.get("n_core", ray_data.get("core_refractive_index"))
    n_clad = ray_data.get(
        "n_cladding", ray_data.get("cladding_refractive_index")
    )
    if n_core is not None and n_clad is not None:
        subtitle_parts.append(
            f"n_core={float(n_core):.3f}, n_clad={float(n_clad):.3f}"
        )
    if ray_data.get("incident_angle_deg") is not None:
        subtitle_parts.append(
            f"θ_in={float(ray_data['incident_angle_deg']):.1f}°"
        )
    if ray_data.get("acceptance_angle_deg") is not None:
        subtitle_parts.append(
            f"θ_a={float(ray_data['acceptance_angle_deg']):.1f}°"
        )
    if ray_data.get("critical_angle_deg") is not None:
        subtitle_parts.append(
            f"θ_c={float(ray_data['critical_angle_deg']):.1f}°"
        )

    subtitle_text = " | ".join(subtitle_parts)

    fig.update_layout(
        title={
            "text": f"Optical Fiber Ray Propagation<br><sup>{subtitle_text}</sup>",
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis={
            "title": "Axial Distance z (μm)",
            "range": [min(-0.1 * length, inc_x_min * 1.1), length * 1.05],
            "zeroline": True,
            "showgrid": True,
        },
        yaxis={
            "title": "Radial Position r (μm)",
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
