import pytest

from physics.fiber_geometry import simulate_fiber_ray


def test_guided_ray_is_returned_for_small_launch_angle():
    result = simulate_fiber_ray(1.48, 1.46, launch_angle_deg=5)
    assert result["is_tir"] is True
    assert len(result["propagating_ray"]["x"]) == 400


def test_escaping_ray_has_refracted_overlay():
    result = simulate_fiber_ray(1.48, 1.46, launch_angle_deg=25)
    assert result["is_tir"] is False
    assert "refracted_ray" in result


def test_invalid_refractive_indices_rejected():
    with pytest.raises(ValueError):
        simulate_fiber_ray(1.4, 1.5)
