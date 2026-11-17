import pytest

from physics.signal_propagation import broaden_gaussian_pulse


def test_zero_dispersion_preserves_width_and_shape():
    times = [-2.0, -1.0, 0.0, 1.0, 2.0]
    _, output, width = broaden_gaussian_pulse(times, 1.0, 0.0, 50.0)
    assert width == pytest.approx(1.0)
    assert output[2] == pytest.approx(1.0)


def test_dispersion_broadens_pulse():
    _, _, width = broaden_gaussian_pulse([0.0], 1e-12, 20e-24, 50.0)
    assert width > 1e-12


def test_invalid_pulse_width():
    with pytest.raises(ValueError):
        broaden_gaussian_pulse([0.0], 0.0, 1.0, 1.0)
