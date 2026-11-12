import pytest
from plotly.graph_objects import Figure

from visualization.fiber_animation import create_fiber_ray_figure


@pytest.fixture
def sample_ray_data():
    return {
        "core_radius": 4.0,
        "cladding_radius": 6.0,
        "fiber_length": 30.0,
        "core_refractive_index": 1.48,
        "cladding_refractive_index": 1.46,
        "incident_angle_deg": 20,
        "incident_ray": {
            "x": [0, 2],
            "y": [5, 3],
        },
        "reflected_rays": [
            {"x": [2, 10, 18], "y": [3, -3, 3]},
            {"x": [18, 24, 30], "y": [3, -3, 0]},
        ],
    }


def test_create_fiber_ray_figure_returns_plotly_figure(sample_ray_data):
    figure = create_fiber_ray_figure(sample_ray_data)

    assert isinstance(figure, Figure)
    assert figure.layout.title.text == "Optical Fiber Ray Simulation"


def test_create_fiber_ray_figure_contains_expected_traces(sample_ray_data):
    figure = create_fiber_ray_figure(sample_ray_data)

    trace_names = [trace.name for trace in figure.data]
    assert trace_names[:3] == ["Cladding", "Core", "Incident Ray"]
    assert "Reflected Ray" in trace_names


def test_create_fiber_ray_figure_accepts_empty_reflected_paths(sample_ray_data):
    sample_ray_data["reflected_rays"] = []

    figure = create_fiber_ray_figure(sample_ray_data)

    assert len(figure.data) == 3


@pytest.mark.parametrize(
    "bad_data, expected_message",
    [
        ({}, "missing required keys"),
        (
            {
                "core_radius": 2,
                "cladding_radius": 2,
                "fiber_length": 10,
                "incident_ray": {"x": [0, 1], "y": [0, 1]},
                "reflected_rays": [],
            },
            "must be larger than",
        ),
        (
            {
                "core_radius": 2,
                "cladding_radius": 3,
                "fiber_length": 10,
                "incident_ray": {"x": [0], "y": [0]},
                "reflected_rays": [],
            },
            "at least 2 points",
        ),
        (
            {
                "core_radius": 2,
                "cladding_radius": 3,
                "fiber_length": 10,
                "incident_ray": {"x": [0, "bad"], "y": [0, 1]},
                "reflected_rays": [],
            },
            "numeric values",
        ),
    ],
)
def test_create_fiber_ray_figure_validation_errors(bad_data, expected_message):
    with pytest.raises((TypeError, ValueError), match=expected_message):
        create_fiber_ray_figure(bad_data)
