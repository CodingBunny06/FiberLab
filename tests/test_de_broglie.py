import math

import pytest

from physics.de_broglie import (
    PLANCK_CONSTANT,
    de_broglie_wavelength,
    momentum,
    wavelength_from_momentum,
)


def test_electron_wavelength_reference():
    mass = 9.1093837e-31
    velocity = 1e6
    assert de_broglie_wavelength(mass, velocity) == pytest.approx(
        PLANCK_CONSTANT / (mass * velocity)
    )


def test_wavelength_is_inverse_to_momentum():
    p = momentum(1e-27, 1e5)
    assert wavelength_from_momentum(p) == pytest.approx(
        de_broglie_wavelength(1e-27, 1e5)
    )


@pytest.mark.parametrize(
    "mass,velocity", [(0, 1), (-1, 1), (1, 0), (1, math.inf), (True, 1)]
)
def test_invalid_particle_inputs(mass, velocity):
    with pytest.raises((TypeError, ValueError)):
        de_broglie_wavelength(mass, velocity)


def test_rejects_superluminal_speed():
    with pytest.raises(ValueError):
        de_broglie_wavelength(1e-30, 3e8)
