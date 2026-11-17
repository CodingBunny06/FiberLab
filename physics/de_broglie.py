"""De Broglie matter-wave calculations.

The default model is non-relativistic: lambda = h / (m v). The caller is
responsible for presenting the approximation's validity to the user.
"""
from __future__ import annotations

import math

PLANCK_CONSTANT = 6.62607015e-34  # J s
SPEED_OF_LIGHT = 299_792_458.0  # m/s


def _positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number.")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return result


def de_broglie_wavelength(mass_kg: float, velocity_m_s: float) -> float:
    """Return the non-relativistic matter wavelength in metres."""
    mass = _positive_finite(mass_kg, "mass_kg")
    velocity = _positive_finite(velocity_m_s, "velocity_m_s")
    if velocity >= SPEED_OF_LIGHT:
        raise ValueError("Velocity must be below the speed of light.")
    return PLANCK_CONSTANT / (mass * velocity)


def momentum(mass_kg: float, velocity_m_s: float) -> float:
    """Return non-relativistic momentum in kg m/s."""
    mass = _positive_finite(mass_kg, "mass_kg")
    velocity = _positive_finite(velocity_m_s, "velocity_m_s")
    if velocity >= SPEED_OF_LIGHT:
        raise ValueError("Velocity must be below the speed of light.")
    return mass * velocity


def wavelength_from_momentum(momentum_kg_m_s: float) -> float:
    """Return wavelength for a supplied positive momentum."""
    p = _positive_finite(momentum_kg_m_s, "momentum_kg_m_s")
    return PLANCK_CONSTANT / p
