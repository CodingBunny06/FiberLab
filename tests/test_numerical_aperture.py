"""Tests for core optical-fiber calculations."""

import math

import pytest

from physics.numerical_aperture import (
    calculate_acceptance_angle,
    calculate_critical_angle,
    calculate_numerical_aperture,
    is_total_internal_reflection,
)


def test_core_calculations_match_reference_values():
    n_core, n_cladding = 1.5, 1.4

    assert calculate_numerical_aperture(n_core, n_cladding) == pytest.approx(
        math.sqrt(0.29)
    )
    assert calculate_critical_angle(n_core, n_cladding) == pytest.approx(
        math.asin(1.4 / 1.5)
    )
    assert calculate_acceptance_angle(n_core, n_cladding) == pytest.approx(
        math.asin(math.sqrt(0.29))
    )


@pytest.mark.parametrize(
    "n_core,n_cladding",
    [
        (0, 1.0),
        (-1.0, 1.0),
        (1.0, 0),
        (1.4, 1.5),
        (1.5, 1.5),
        (float("nan"), 1.4),
        (1.5, float("inf")),
        ("1.5", 1.4),
        (True, 1.4),
    ],
)
def test_refractive_index_validation(n_core, n_cladding):
    with pytest.raises(ValueError):
        calculate_numerical_aperture(n_core, n_cladding)

    with pytest.raises(ValueError):
        calculate_critical_angle(n_core, n_cladding)


def test_acceptance_angle_rejects_impossible_air_angle():
    with pytest.raises(ValueError):
        calculate_acceptance_angle(2.0, 1.0)


@pytest.mark.parametrize(
    "incidence_angle,expected",
    [
        (0.5, False),
        (math.asin(1.4 / 1.5), False),
        (1.3, True),
        (math.pi / 2, True),
    ],
)
def test_total_internal_reflection_boundary(incidence_angle, expected):
    critical_angle = calculate_critical_angle(1.5, 1.4)
    assert is_total_internal_reflection(incidence_angle, critical_angle) is expected


@pytest.mark.parametrize(
    "incidence_angle,critical_angle",
    [
        (-0.1, 1.0),
        (math.pi / 2 + 0.1, 1.0),
        (float("nan"), 1.0),
        (1.0, 0.0),
        (1.0, float("inf")),
        (True, 1.0),
    ],
)
def test_total_internal_reflection_rejects_invalid_angles(
    incidence_angle, critical_angle
):
    with pytest.raises(ValueError):
        is_total_internal_reflection(incidence_angle, critical_angle)
