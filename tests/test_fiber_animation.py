"""Unit tests for visualization/fiber_animation.py."""

from __future__ import annotations

import inspect
import math
from typing import Any

import plotly.graph_objects as go
import pytest

from visualization.fiber_animation import create_fiber_ray_figure


@pytest.fixture
def tir_ray_data() -> dict[str, Any]:
    """Provide a valid Total Internal Reflection (TIR) ray_data payload."""
    return {
        "core_radius": 25.0,
        "cladding_radius": 62.5,
        "fiber_length": 200.0,
        "incident_ray": {
            "x": [-20.0, 0.0],
            "y": [-10.0, 0.0],
        },
        "propagating_ray": {
            "x": [0.0, 50.0, 150.0, 200.0],
            "y": [0.0, 25.0, -25.0, 0.0],
        },
        "is_tir": True,
        "n_core": 1.48,
        "n_cladding": 1.46,
        "incident_angle_deg": 8.0,
        "acceptance_angle_deg": 14.0,
        "critical_angle_deg": 80.6,
    }


@pytest.fixture
def non_tir_ray_data(tir_ray_data: dict[str, Any]) -> dict[str, Any]:
    """Provide a valid non-TIR (refraction / cladding loss) ray_data payload."""
    data = dict(tir_ray_data)
    data["is_tir"] = False
    data["incident_angle_deg"] = 22.0
    data["refracted_rays"] = [
        {"x": [50.0, 90.0], "y": [25.0, 62.5]},
        {"x": [150.0, 190.0], "y": [-25.0, -62.5]},
    ]
    return data


def test_returns_plotly_figure(tir_ray_data: dict[str, Any]) -> None:
    """1. Verify create_fiber_ray_figure returns a valid Plotly Figure object."""
    fig = create_fiber_ray_figure(tir_ray_data)
    assert isinstance(fig, go.Figure)


def test_core_and_cladding_shapes_present(tir_ray_data: dict[str, Any]) -> None:
    """2. Verify core and cladding rectangular geometry shapes are rendered."""
    fig = create_fiber_ray_figure(tir_ray_data)
    assert len(fig.layout.shapes) == 2
    shape_names = {shape.name for shape in fig.layout.shapes}
    assert "Core Region" in shape_names
    assert "Cladding Boundary" in shape_names


def test_tir_labeling_and_traces(tir_ray_data: dict[str, Any]) -> None:
    """3. Verify TIR regime trace labels, reflection points, and title text."""
    fig = create_fiber_ray_figure(tir_ray_data)
    trace_names = [trace.name for trace in fig.data if trace.name]
    assert "Incident Launch Ray" in trace_names
    assert "Guided Ray (TIR)" in trace_names
    assert "Interface Reflection Points" in trace_names
    assert "Regime: Total Internal Reflection (TIR)" in fig.layout.title.text


def test_non_tir_labeling_and_refracted_rays(
    non_tir_ray_data: dict[str, Any],
) -> None:
    """4. Verify non-TIR regime labels and refracted cladding loss traces."""
    fig = create_fiber_ray_figure(non_tir_ray_data)
    trace_names = [trace.name for trace in fig.data if trace.name]
    assert "Refracted Cladding Loss" in trace_names
    assert "Attenuated Ray (Refracted)" in trace_names
    assert "Regime: Refraction / Cladding Loss" in fig.layout.title.text


def test_optional_metadata_in_subtitle(tir_ray_data: dict[str, Any]) -> None:
    """5. Verify optional optical metadata appears formatted in the figure title."""
    fig = create_fiber_ray_figure(tir_ray_data)
    title_text = fig.layout.title.text
    assert "n_core=1.480" in title_text
    assert "n_clad=1.460" in title_text
    assert "θ_in=8.0°" in title_text
    assert "θ_a=14.0°" in title_text
    assert "θ_c=80.6°" in title_text


def test_accepts_tuple_coordinate_sequences(
    tir_ray_data: dict[str, Any],
) -> None:
    """6. Verify ray paths and reflection_points work with (x, y) tuple sequences."""
    tir_ray_data["incident_ray"] = [(-20.0, -10.0), (0.0, 0.0)]
    tir_ray_data["propagating_ray"] = [(0.0, 0.0), (50.0, 25.0), (100.0, 0.0)]
    tir_ray_data["reflection_points"] = [(50.0, 25.0)]
    fig = create_fiber_ray_figure(tir_ray_data)
    assert isinstance(fig, go.Figure)


def test_rejects_non_mapping_input() -> None:
    """7. Verify non-mapping ray_data raises TypeError."""
    with pytest.raises(TypeError, match="ray_data must be a dictionary-like Mapping"):
        create_fiber_ray_figure(["not", "a", "dict"])  # type: ignore[arg-type]


def test_rejects_missing_required_keys(tir_ray_data: dict[str, Any]) -> None:
    """8. Verify missing any required contract key raises ValueError."""
    for missing_key in (
        "core_radius",
        "cladding_radius",
        "fiber_length",
        "incident_ray",
        "propagating_ray",
        "is_tir",
    ):
        payload = dict(tir_ray_data)
        del payload[missing_key]
        with pytest.raises(ValueError, match="Missing required keys in ray_data"):
            create_fiber_ray_figure(payload)


def test_rejects_non_positive_dimensions(tir_ray_data: dict[str, Any]) -> None:
    """9. Verify zero or negative fiber geometry dimensions raise ValueError."""
    for key, bad_value in (
        ("core_radius", 0.0),
        ("core_radius", -5.0),
        ("cladding_radius", -10.0),
        ("fiber_length", 0.0),
    ):
        payload = dict(tir_ray_data, **{key: bad_value})
        with pytest.raises(ValueError, match="must be a finite positive number"):
            create_fiber_ray_figure(payload)


def test_rejects_cladding_not_greater_than_core(
    tir_ray_data: dict[str, Any],
) -> None:
    """10. Verify cladding_radius <= core_radius raises ValueError."""
    tir_ray_data["cladding_radius"] = tir_ray_data["core_radius"]
    with pytest.raises(
        ValueError,
        match="cladding_radius must be strictly greater than core_radius",
    ):
        create_fiber_ray_figure(tir_ray_data)


def test_rejects_nan_and_infinity_inputs(tir_ray_data: dict[str, Any]) -> None:
    """11. Verify NaN and infinity values in dimensions, rays, or metadata raise ValueError."""
    for bad_num in (math.nan, math.inf, -math.inf):
        bad_dim = dict(tir_ray_data, core_radius=bad_num)
        with pytest.raises(ValueError, match="finite"):
            create_fiber_ray_figure(bad_dim)

        bad_ray = dict(
            tir_ray_data,
            incident_ray={"x": [0.0, bad_num], "y": [0.0, 1.0]},
        )
        with pytest.raises(ValueError, match="finite"):
            create_fiber_ray_figure(bad_ray)

        bad_meta = dict(tir_ray_data, n_core=bad_num)
        with pytest.raises(ValueError, match="finite"):
            create_fiber_ray_figure(bad_meta)


def test_rejects_invalid_or_inconsistent_ray_coordinates(
    tir_ray_data: dict[str, Any],
) -> None:
    """12. Verify mismatched x/y lengths or fewer than 2 points raise ValueError."""
    mismatched = dict(
        tir_ray_data,
        propagating_ray={"x": [0.0, 50.0, 100.0], "y": [0.0, 25.0]},
    )
    with pytest.raises(ValueError, match="equal length"):
        create_fiber_ray_figure(mismatched)

    too_short = dict(
        tir_ray_data,
        incident_ray={"x": [0.0], "y": [0.0]},
    )
    with pytest.raises(ValueError, match="at least 2 coordinate points"):
        create_fiber_ray_figure(too_short)


def test_invalid_optional_metadata_and_architecture_isolation(
    tir_ray_data: dict[str, Any],
) -> None:
    """13. Verify invalid optional metadata is rejected and module is isolated from Streamlit."""
    bad_indices = dict(tir_ray_data, n_core=1.45, n_cladding=1.48)
    with pytest.raises(
        ValueError,
        match="Core refractive index must be strictly greater than cladding refractive index",
    ):
        create_fiber_ray_figure(bad_indices)

    import visualization.fiber_animation as mod

    source = inspect.getsource(mod)
    assert "import streamlit" not in source
    assert "from streamlit" not in source
